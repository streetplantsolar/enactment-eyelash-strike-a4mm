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
import smtplib, ssl


### Build the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], title="IVCurves.com")
server = app.server

# =============================================================================
# dash.register_page(__name__,
#                    path='/',
#                    name='Home',
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

###Analyze things
irradiance_slider = dcc.Slider(0,1200,50, value=1000, marks=None,tooltip={"placement":"bottom", "always_visible":True})
temperature_slider = dcc.Slider(-25,70,5, value=25, marks=None,tooltip={"placement":"bottom", "always_visible":True})

### Contact Form ###
# =============================================================================
# email_input = dbc.Row([
#         dbc.Label("Email"
#                 , html_for="example-email-row"
#                 , width=2),
#         dbc.Col(dbc.Input(
#                 type="email"
#                 , id="example-email-row"
#                 , placeholder="Email"
#             ),width=10,
#         )],className="mb-3"
# )
# 
# user_input = dbc.Row([
#         dbc.Label("Name", html_for="example-name-row", width=2),
#         dbc.Col(
#             dbc.Input(
#                 type="text"
#                 , id="example-name-row"
#                 , placeholder="Name"
#                 , maxLength = 80
#             ),width=10
#         )], className="mb-3"
# )
# 
# message = dbc.Row([
#         dbc.Label("Message", html_for="example-message-row", width=2)
#         ,dbc.Col(
#             dbc.Textarea(id = "example-message-row"
#                 , className="mb-3"
#                 , placeholder="Message"
#                 , required = True)
#             , width=10)
#         ], className="mb-3")
# 
# def contact_form():
#     markdown = ''' # We'd love to hear from you! '''   
#     form = html.Div([ dbc.Container([
#             dcc.Markdown(markdown)
#             , html.Br()
#             , dbc.Card(
#                 dbc.CardBody([
#                      dbc.Form([email_input
#                         , user_input
#                         , message])
#                 ,html.Div(id = 'div-button', children = [
#                     dbc.Button('Submit'
#                     , color = 'primary'
#                     , id='button-submit'
#                     , n_clicks=0)
#                 ]) #end div
#                 ])#end cardbody
#             )#end card
#             , html.Br()
#             , html.Br()
#         ])
#         ])
#     return form
# 
# 
# =============================================================================
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
                                html.H5('Manufacturer:'),
                                dropdown_manuf,
                                html.Hr(),
                                html.H5("Model:"),
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
                    "Analyze",
                    id="analyze_button"
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
                            ]
                        )
                    ),
                    id="analyze_collapse",
                    is_open=False
                ),
                html.Hr(),
            ], width=3),
            dbc.Col([
                dcc.Graph(id='display', style={'height': '80vh'}),
            ], width=9, align="start")
        ]),
        html.Hr(),
        #contact_form()
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

### Callback to make analyze menu expand
@app.callback(
    Output("analyze_collapse", "is_open"),
    [Input("analyze_button", "n_clicks")],
    [State("analyze_collapse", "is_open")]
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
    Input(temperature_slider, 'value')
)

@app.callback(Output('div-button', 'children'),
     Input("button-submit", 'n_clicks')
     ,Input("example-email-row", 'value')
     ,Input("example-name-row", 'value')
     ,Input("example-message-row", 'value')
    )
# =============================================================================
# def submit_message(n, email, name, message):
#     port = 465  # For SSL
#     sender_email = email
#     receiver_email = 'streetplantsolar@gmail.com'
#     context = ssl.create_default_context()       
#     if n > 0:
#         with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#             server.login("streetplantsolar@gmail.com", 'F00rpkcahSPS!')
#             server.sendmail(sender_email, receiver_email, message)
#             server.quit()
#         return [html.P("Message Sent")]
#     else:
#         return[dbc.Button('Submit', color = 'primary', id='button-submit', n_clicks=0)]
# =============================================================================

def update_graph(selected_mod, selected_option, selected_irradiance, selected_temperature):
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

    df_V = pd.DataFrame(curve_info['v'].transpose(), columns=['Voltage'])
    df_I = pd.DataFrame(curve_info['i'].transpose(), columns=['Current'])
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
                go.Scatter(
                    x=df_V.loc[:,"Voltage"],
                    y=df_I.loc[:,"Current"],
                    mode="lines",
                    line_color="deepskyblue",
                    showlegend=False,
                    )
                )   
    fig.update_xaxes(title_text="Voltage")
    fig.update_yaxes(title_text="Current", secondary_y=False)
    
    if selected_option == "Pmp":
        df_Vmp = pd.DataFrame(curve_info['v_mp'].transpose(), columns=['Vmp'])
        df_Imp = pd.DataFrame(curve_info['i_mp'].transpose(), columns=['Imp'])
     
        fig.add_trace(
            go.Scatter(
                x=df_Vmp.loc[:,"Vmp"],
                y=df_Imp.loc[:,"Imp"],
                line_color="red",
                showlegend=False),
            secondary_y=False
            )
    
    if selected_option == "Power Curve":
        df_V['Power'] = df_V['Voltage'] * df_I['Current']
        fig.add_trace(
             go.Scatter(
                 x=df_V.loc[:,"Voltage"],
                 y=df_V.loc[:,"Power"],
                 mode="lines",
                 line_color="goldenrod",
                 showlegend=False),
             secondary_y=True
             )
        fig.update_yaxes(title_text="Power", secondary_y=True)

    return fig

if __name__=='__main__':
    app.run_server(port=8053, debug=False)
