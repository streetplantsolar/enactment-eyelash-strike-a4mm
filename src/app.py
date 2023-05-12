import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import Dash, dcc, Output, Input, State, dash_table, callback
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import pvlib


### Build the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], title="IVCurves.com")
server = app.server

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
      <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y8DJHVNDS6"></script>
      <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-Y8DJHVNDS6');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

# =============================================================================
# dash.register_page(__name__,
#                    title='IVCurves.com',
#                    description='PV solar IV curve database and analysis tool. Access and analyze nearly 17,000 modules from 200 manufacturers.'
#                    )
# =============================================================================

###Module things
mod_db = pd.read_csv('module_db.csv')
dropdown_manuf = dcc.Dropdown(options=mod_db.loc[:,'Manufacturer'].unique(),
                        clearable=False)
dropdown_mod = dcc.Dropdown(options=[])

temp_cell = 25
effective_irradiance = 1000


###Parameter things
dropdown_parameters = dcc.Dropdown(options=['Pmp', 'Power Curve'],
                        clearable=True)

###Scale things
irradiance_slider = dcc.Slider(0,1200,50, value=1000, marks=None,tooltip={"placement":"bottom", "always_visible":True})
temperature_slider = dcc.Slider(-25,70,5, value=25, marks=None,tooltip={"placement":"bottom", "always_visible":True})
string_input = dbc.Input(type="number", value=1, min=1, max=50, step=1)

###Compare things
df_compare = pd.DataFrame(columns=['Voltage', 'Current'], index=range(10))
compare_input = dash_table.DataTable(
    id='compare-input',
    columns = [{'name': col, 'id':col} for col in df_compare.columns],
    data = df_compare.to_dict('records'),
    editable=True,
    )

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                dcc.Markdown("""
                # IV Curve Database & Analysis
                """)
            ], width=True),
        ], align="end"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Select Module",
                    id="module_button"
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6('Manufacturer:'),
                                dropdown_manuf,
                                html.Hr(),
                                html.H6("Model:"),
                                dropdown_mod,
                            ]
                        )
                    ),
                    id="module_collapse",
                    is_open=False
                ),
                html.Hr(),
                dbc.Button(
                    "Add Parameters",
                    id="parameter_button"
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            dropdown_parameters,
                        )
                    ),
                    id="parameter_collapse",
                    is_open=False
                ),
                html.Hr(),
                dbc.Button(
                    "Scale",
                    id="scale_button"
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Irradiance (W/m2)"),
                                irradiance_slider,
                                html.Hr(),
                                html.H6("Temperature (°C)"),
                                temperature_slider,
                                html.Hr(),
                                html.H6("Modules per String"),
                                string_input
                            ]
                        )
                    ),
                    id="scale_collapse",
                    is_open=False
                ),
                html.Hr(),
                dbc.Button(
                    "Plot your data",
                    id="compare_button"
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                compare_input
                            ]
                        )
                    ),
                    id="compare_collapse",
                    is_open=False
                ),
            ], width=3),
            dbc.Col([
                dcc.Graph(id='display', style={'height': '80vh'}),
            ], width=9, align="start")
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Contact Us",
                    id="contact_button"
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Iframe(
                                    src='https://docs.google.com/forms/d/e/1FAIpQLSe9bizwPKrj5Oaeehhruycgtr7MFDlNSyT3vLJupQnv89QD4g/viewform?embedded=true',
                                    width='1000px',
                                    height='800px',
                                    )
                            ]
                        )
                    ),
                    id="contact_collapse",
                    is_open=False
                ),
            ])
        ]),
        html.Hr(),
        dcc.Markdown("""
          © 2023 StreetPlant Solar. All Rights Reserved.           
                     """)   
        
    ],
    fluid=True
)
                                                   
### Callback to update Model dropdown based on Manufacturer                          
@app.callback(
    Output(dropdown_mod,'options'),
    Input(dropdown_manuf, 'value')
    )
def update_dropdown_mod(selected_manuf):
    dff=mod_db.loc[mod_db['Manufacturer'].str.contains(selected_manuf)]
    mods_of_manuf = dff.Model                   
    return mods_of_manuf

@app.callback(
    Output(dropdown_mod,'value'),
    Input(dropdown_mod, 'options')
    )
def update_mod_value(mods_of_manuf):
    return mods_of_manuf[0]['value']
 
### Callback to make module select menu expand
@app.callback(
    Output("module_collapse", "is_open"),
    [Input("module_button", "n_clicks")],
    [State("module_collapse", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open                             
                                                    
### Callback to make parameters menu expand
@app.callback(
    Output("parameter_collapse", "is_open"),
    [Input("parameter_button", "n_clicks")],
    [State("parameter_collapse", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

### Callback to make scale menu expand
@app.callback(
    Output("scale_collapse", "is_open"),
    [Input("scale_button", "n_clicks")],
    [State("scale_collapse", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

### Callback to make scale menu expand
@app.callback(
    Output("compare_collapse", "is_open"),
    [Input("compare_button", "n_clicks")],
    [State("compare_collapse", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

### Callback to make contact menu expand
@app.callback(
    Output("contact_collapse", "is_open"),
    [Input("contact_button", "n_clicks")],
    [State("contact_collapse", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("display", component_property='figure'),
    Input(dropdown_mod, 'value'),
    Input(dropdown_parameters, 'value'),
    Input(irradiance_slider, 'value'),
    Input(temperature_slider, 'value'),
    Input(string_input, 'value'),
    Input(compare_input,'data'),
)


def update_graph(selected_mod, selected_option, selected_irradiance, selected_temperature, mods_per_string, data):
    df = mod_db[mod_db['Model'].str.match(selected_mod)]
    df=df.iloc[0,:]
    
    cecparams = pvlib.pvsystem.calcparams_cec(
        effective_irradiance=selected_irradiance,
        temp_cell=selected_temperature,
        alpha_sc=df.alpha_sc,
        a_ref=df.a_ref,
        I_L_ref=df.I_L_ref,
        I_o_ref=df.I_o_ref,
        R_sh_ref=df.R_sh_ref,
        R_s=df.R_s,
        Adjust=df.Adjust,
        EgRef=1.121,
        dEgdT=-0.0002677
        )
    IL, I0, Rs, Rsh, nNsVth = cecparams
    curve_info = pvlib.pvsystem.singlediode(
        photocurrent=IL.flatten(),
        saturation_current=I0.flatten(),
        resistance_series=Rs,
        resistance_shunt=Rsh.flatten(),
        nNsVth=nNsVth.flatten(),
        ivcurve_pnts=101,
        method='lambertw')                    

    df = pd.DataFrame(curve_info['v'].transpose(), columns=['Voltage'])
    df['Voltage'] = df['Voltage']*mods_per_string
    df['Current'] = pd.DataFrame(curve_info['i'].transpose(), columns=['Current'])
    df['Power'] = df['Voltage'] * df['Current']
    df_Vmp = pd.DataFrame(curve_info['v_mp'].transpose(), columns=['Vmp'])
    df_Vmp *= mods_per_string
    df_Imp = pd.DataFrame(curve_info['i_mp'].transpose(), columns=['Imp'])
   
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
                go.Scatter(
                    x=df.loc[:,"Voltage"],
                    y=df.loc[:,"Current"],
                    name="Modeled IV",
                    mode="lines",
                    line_color="#78c2ad",
                    showlegend=False,
                    )
                )   
    fig.update_xaxes(title_text="Voltage (V)")
    fig.update_yaxes(title_text="Current (A)", secondary_y=False)
    fig.update_layout(hovermode="closest")
    
    if selected_option == "Pmp":     
        fig.add_trace(
            go.Scatter(
                x=df_Vmp.loc[:,"Vmp"],
                y=df_Imp.loc[:,"Imp"],
                name="Pmp",
                line_color="#007bff",
                showlegend=False),
            secondary_y=False
            )
    
    if selected_option == "Power Curve":
        fig.add_trace(
             go.Scatter(
                 x=df.loc[:,"Voltage"],
                 y=df.loc[:,"Power"],
                 name="Modeled Power",
                 mode="lines",
                 line_color="#f3969a",
                 showlegend=False),
             secondary_y=True
             )
        fig.update_yaxes(title_text="Power (W)", secondary_y=True)
    
    df_compare = pd.DataFrame.from_dict(data)
    
    fig.add_trace(
            go.Scatter(
               x=df_compare.loc[:,"Voltage"],
               y=df_compare.loc[:,"Current"],
               name="Your module",
               mode="lines",
               line_color="#ffce67",
               showlegend=False),
            secondary_y=False
            )
    return fig

if __name__=='__main__':
    app.run_server(port=8053, debug=False)
