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
import datetime
from datetime import date
import math


### Build the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], title="IVCurves.com")
server = app.server

meta_description = "PV solar IV curve database and analysis tool. Explore thousands of module performance data from LONGi, Trina, Jinko, Canadian Solar, and more."
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        <!-- Add the meta description -->
        <meta name="description" content="{meta_description}">
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y8DJHVNDS6"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());

            gtag('config', 'G-Y8DJHVNDS6');
        </script>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

# Module database
mod_db = pd.read_csv('module_db.csv')
dropdown_manuf = dcc.Dropdown(options=mod_db['Manufacturer'].unique(), value='LONGi Green Energy Technology Co. Ltd.', clearable=False)
dropdown_mod = dcc.Dropdown(options=[])

temp_cell = 25
effective_irradiance = 1000


# Parameter dropdown
dropdown_parameters = dcc.Dropdown(options=['Pmp', 'Power Curve'], clearable=True)


# Scale inputs
irradiance_input = dbc.Input(type="number", value=1000, min=0, max=1500, step=0.01)
temperature_input = dbc.Input(type="number", value=25, min=-100, max=100, step=0.01)
string_input = dbc.Input(type="number", value=1, min=1, max=50, step=1)

# Degrade inputs
today = datetime.date.today()
degradation_date_picker = dcc.DatePickerRange(id='degradation-date-range', 
                                             start_date=date(today.year, today.month, today.day), clearable=True,
                                             end_date=date(today.year, today.month, today.day))
degradation_input = dbc.Input(type="number", value=0.5, min=0, max=100, step=0.01)

# Compare data input
df_compare = pd.DataFrame(columns=['Voltage', 'Current'], index=range(10))
compare_input = dash_table.DataTable(
    id='compare-input',
    columns=[{'name': col, 'id': col, 'type': 'numeric'} for col in df_compare.columns],
    data=df_compare.to_dict('records'),
    editable=True,
    style_table={'textAlign': 'center'},
    style_cell={'textAlign': 'center'},
    style_header={'textAlign': 'center'},
)

# App layout
app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                dcc.Markdown("# IV Curve Database & Analysis Tool")
            ], width=True),
        ], align="end"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Button("Select module", id="module_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([
                            html.H6('Manufacturer:'),
                            dropdown_manuf,
                            html.Hr(),
                            html.H6("Model:"),
                            dropdown_mod,
                            html.Hr(),
                            dbc.Row([  # Create a row for Irradiance, Temperature, and Modules per String
                                dbc.Col([html.H6("Irradiance (W/m2)"), irradiance_input], width=4),
                                dbc.Col([html.H6("Temperature (°C)"), temperature_input], width=4),
                                dbc.Col([html.H6("Modules per String"), string_input], width=4),
                            ]),
                            html.Hr(),
                            dbc.Row([  # Create DataTable for Pmp, Isc, Voc, Imp, Vmp
                                dbc.Col(dash_table.DataTable(
                                    id='module-parameters-table',
                                    columns=[{'name': col, 'id': col, 'type': 'numeric'} for col in ["Pmp", "Isc", "Voc", "Imp", "Vmp"]],
                                    data=[{}],
                                    style_table={'textAlign': 'center'},
                                    style_cell={'textAlign': 'center'},
                                    style_header={'textAlign': 'center'},
                                ), width=12),
                            ]),
                        ])
                    ),
                    id="module_collapse",
                    is_open=False
                ),
                html.Hr(),
                dbc.Button("Add parameters", id="parameter_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(dropdown_parameters),
                    ),
                    id="parameter_collapse",
                    is_open=False
                ),
                html.Hr(),
                dbc.Button("Degrade", id="degrade_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([
                            html.H6("Install Date --> Measurement Date"),
                            degradation_date_picker,
                            html.Hr(),
                            html.H6("Expected Degradation (%/year):"),
                            degradation_input
                        ])
                    ),
                    id="degrade_collapse",
                    is_open=False
                ),
                html.Hr(),
                dbc.Button("Plot your data", id="compare_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([compare_input]),
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
                dbc.Button("Q&A", id="QA_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("What is an IV Curve?"),
                            html.H6("A solar PV (Photovoltaic) IV curve, also known as an I-V curve, is a graphical representation of the electrical characteristics of a photovoltaic module or solar panel. It illustrates the relationship between the current (I) generated by the solar panel and the voltage (V) across its terminals under varying conditions, such as different levels of sunlight and temperature. Analyzing a solar PV IV curve helps assess the module's efficiency, performance, and its ability to generate electricity under different environmental conditions, making it a crucial tool for evaluating and optimizing solar energy systems.")
                        ])
                    ),
                    id="QA_collapse",
                    is_open=False
                ),
            ])
        ]),

        html.Hr(),

        dbc.Row([
            dbc.Col([
                dbc.Button("Contact Us", id="contact_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([
                            html.Iframe(
                                src='https://docs.google.com/forms/d/e/1FAIpQLSe9bizwPKrj5Oaeehhruycgtr7MFDlNSyT3vLJupQnv89QD4g/viewform?embedded=true',
                                width='1000px',
                                height='800px',
                            )
                        ])
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
                                                   
# Callbacks
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

menus = ["module", "parameter", "degrade", "compare", "QA", "contact"]
for menu in menus:
    app.callback(
        Output(f"{menu}_collapse", "is_open"),
        [Input(f"{menu}_button", "n_clicks")],
        [State(f"{menu}_collapse", "is_open")]
    )(toggle_collapse)

@app.callback(
    Output(dropdown_mod, 'options'),
    Input(dropdown_manuf, 'value')
)
def update_dropdown_mod(selected_manuf):
    dff = mod_db.loc[mod_db['Manufacturer'].str.contains(selected_manuf)]
    mods_of_manuf = dff.Model
    return mods_of_manuf

@app.callback(
    Output(dropdown_mod, 'value'),
    Input(dropdown_mod, 'options')
)
def update_mod_value(mods_of_manuf):
    return mods_of_manuf[0]['value']

@app.callback(
    Output('module-parameters-table', 'data'),
    Input(dropdown_mod, 'value')
)
def update_module_parameters(selected_mod):
    if selected_mod:
        module_data = mod_db[mod_db['Model'] == selected_mod]

        if not module_data.empty:
            pmp = module_data.iloc[0]['STC']
            isc = module_data.iloc[0]['I_sc_ref']
            voc = module_data.iloc[0]['V_oc_ref']
            imp = module_data.iloc[0]['I_mp_ref']
            vmp = module_data.iloc[0]['V_mp_ref']
            data = [{'Pmp': pmp, 'Isc': isc, 'Voc': voc, 'Imp': imp, 'Vmp': vmp}]
            return data

    return [{}]

@app.callback(
    Output("display", component_property='figure'),
    [
        Input(dropdown_mod, 'value'),
        Input(dropdown_parameters, 'value'),
        Input(irradiance_input, 'value'),
        Input(temperature_input, 'value'),
        Input(string_input, 'value'),
        Input(degradation_date_picker, 'start_date'),
        Input(degradation_date_picker, 'end_date'),
        Input(degradation_input, 'value'),
        Input(compare_input, 'data'),
    ]
)

def update_graph(selected_mod, selected_option, selected_irradiance, selected_temperature, mods_per_string, start_date, end_date, input_degradation_rate, data):
    selected_module_data = mod_db[mod_db['Model'].str.match(selected_mod)].iloc[0, :]

    cec_params = {
        'effective_irradiance': selected_irradiance,
        'temp_cell': selected_temperature,
        'alpha_sc': selected_module_data.alpha_sc,
        'a_ref': selected_module_data.a_ref,
        'I_L_ref': selected_module_data.I_L_ref,
        'I_o_ref': selected_module_data.I_o_ref,
        'R_sh_ref': selected_module_data.R_sh_ref,
        'R_s': selected_module_data.R_s,
        'Adjust': selected_module_data.Adjust,
        'EgRef': 1.121,
        'dEgdT': -0.0002677
    }
    IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(**cec_params)

    curve_info = pvlib.pvsystem.singlediode(
        photocurrent=IL.flatten(),
        saturation_current=I0.flatten(),
        resistance_series=Rs,
        resistance_shunt=Rsh.flatten(),
        nNsVth=nNsVth.flatten(),
        ivcurve_pnts=101,
        method='lambertw'
    )

    degradation = 1
    if start_date and end_date:
        start_date_object = date.fromisoformat(start_date)
        end_date_object = date.fromisoformat(end_date)
        degradation_days = (end_date_object - start_date_object).days
        if degradation_days > 0:
            degradation = 1 - (input_degradation_rate / 100 * degradation_days / 365.25)

    df_curve = pd.DataFrame(curve_info['v'].transpose(), columns=['Voltage'])
    df_curve['Voltage'] *= mods_per_string * math.sqrt(degradation)

    df_curve['Current'] = pd.DataFrame(curve_info['i'].transpose(), columns=['Current'])
    df_curve['Current'] *= math.sqrt(degradation)

    df_curve['Power'] = df_curve['Voltage'] * df_curve['Current']

    df_Vmp = pd.DataFrame(curve_info['v_mp'].transpose(), columns=['Vmp'])
    df_Vmp *= mods_per_string * math.sqrt(degradation)

    df_Imp = pd.DataFrame(curve_info['i_mp'].transpose(), columns=['Imp'])
    df_Imp *= math.sqrt(degradation)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_curve['Voltage'],
            y=df_curve['Current'],
            name="Modeled IV",
            mode="lines",
            line_color="#78c2ad",
            showlegend=False
        )
    )
    fig.update_xaxes(title_text="Voltage (V)")
    fig.update_yaxes(title_text="Current (A)", secondary_y=False)
    fig.update_layout(hovermode="closest")

    if selected_option == "Pmp":
        fig.add_trace(
            go.Scatter(
                x=df_Vmp['Vmp'],
                y=df_Imp['Imp'],
                name="Pmp",
                line_color="#007bff",
                showlegend=False
            ),
            secondary_y=False
        )

    if selected_option == "Power Curve":
        fig.add_trace(
            go.Scatter(
                x=df_curve['Voltage'],
                y=df_curve['Power'],
                name="Modeled Power",
                mode="lines",
                line_color="#f3969a",
                showlegend=False
            ),
            secondary_y=True
        )
        fig.update_yaxes(title_text="Power (W)", secondary_y=True)

    df_compare = pd.DataFrame.from_dict(data)

    fig.add_trace(
        go.Scatter(
            x=df_compare['Voltage'],
            y=df_compare['Current'],
            name="Your module",
            mode="lines",
            line_color="#ffce67",
            showlegend=False
        ),
        secondary_y=False
    )

    return fig

if __name__=='__main__':
    app.run_server(port=8053, debug=False)
