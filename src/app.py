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

# Set up the app's navigation bar with links to the "Home" and "FAQ" pages
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home/")),
        dbc.NavItem(dbc.NavLink("FAQ", href="/faq")),
        dbc.NavItem(dbc.NavLink("Contact", href="/contact"))
    ],
    brand=html.Div("IVCurves.com", style={"margin-left": "15px"}),  # Adjust margin as needed
    brand_href="/home",
    color="primary",
    dark=True,
)

# App layout
# Define the app layout and include the "Home" and "FAQ" pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Define your app's "FAQ" page layout
faq_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Markdown("# FAQ")
        ], width=True),
    ], align="end"),
    html.Hr(),
    dbc.Row([
        html.H5("What is an IV Curve?"),
        html.H6("A solar PV (Photovoltaic) IV curve, also known as an I-V curve, is a graphical representation of the electrical characteristics of a photovoltaic module or solar panel. It illustrates the relationship between the current (I) generated by the solar panel and the voltage (V) across its terminals under varying conditions, such as different levels of sunlight and temperature. Analyzing a solar PV IV curve helps assess the module's efficiency, performance, and its ability to generate electricity under different environmental conditions, making it a crucial tool for evaluating and optimizing solar energy systems."),
        html.Hr(),
        html.H5("How is a Solar IV Curve Measured?"),
        html.H6("Solar IV curves are typically measured using a specialized piece of equipment called an IV curve tracer. This device applies different voltage levels to the solar panel and records the resulting current."),
        html.Hr(),
        html.H5("What Do the Key Parameters of an IV Curve Mean?"),
        html.H6("Key parameters include Voc (Open-Circuit Voltage), Isc (Short-Circuit Current), and Pmp (Maximum Power Point, or Pmax). Voc is the maximum voltage with no current, Isc is the maximum current with no voltage, and Pmp is the point of maximum power output."),
        html.Hr(),
        html.H5("What Is the Significance of the Open-Circuit Voltage (Voc)?"),
        html.H6("Voc represents the voltage across the solar panel when there is no current flow. It is an essential parameter as it indicates the maximum potential voltage that the solar panel can generate in open-circuit conditions under specific lighting and temperature conditions."),
        html.Hr(),
        html.H5("What Is the Significance of the Short-Circuit Current (Isc)?"),
        html.H6("Isc represents the maximum current that the solar panel can generate when its terminals are short-circuited. This parameter is crucial for assessing the panel's ability to provide high current under specific lighting and temperature conditions."),
        html.Hr(),
        html.H5("What Is the Maximum Power Point (Pmax)?"),
        html.H6("Pmax is the point on the IV curve where the solar panel generates the highest power output. It is the operating point at which the solar panel is most efficient in converting sunlight into electricity."),
        html.Hr(),
        html.H5("What Factors Affect the Shape of an IV Curve?"),
        html.H6("The shape of an IV curve is influenced by factors such as irradiance (intensity of sunlight), temperature, shading, and degradation of the solar panel. Changes in these factors can alter the curve's shape and parameters."),
        html.Hr(),
        html.H5("How Does Temperature Affect the IV Curve?"),
        html.H6("Temperature affects the IV curve by shifting the curve and changing the values of key parameters. Higher temperatures tend to reduce the open-circuit voltage (Voc) and increase the short-circuit current (Isc), impacting the panel's overall performance."),
        html.Hr(),
        html.H5("What Are the Different Operating Points on an IV Curve?"),
        html.H6("An IV curve has various operating points, including open-circuit voltage (Voc), short-circuit current (Isc), and the maximum power point (Pmax). Understanding these points helps in optimizing the performance of a solar panel."),
        html.Hr(),
        html.H5("How Do I Read an IV Curve Graph?"),
        html.H6("To read an IV curve graph, follow the curve's trajectory. The x-axis represents voltage, and the y-axis represents current. The curve starts at Voc, passes through different voltage-current combinations, and peaks at Pmax."),
        html.Hr(),
        html.H5("Why Are IV Curves Important for Solar Panel Testing?"),
        html.H6("IV curves are essential for evaluating a solar panel's performance and efficiency under different conditions. They help identify issues, degradation, and deviations from expected values, ensuring reliable operation."),
        html.Hr(),
        html.H5("How Can IV Curves Help in Diagnosing Solar Panel Issues?"),
        html.H6("IV curves can diagnose issues by revealing deviations from expected curve shapes and parameter values. Irregularities in the curve can indicate shading, damage, degradation, or electrical faults in the panel."),
        html.Hr(),
        html.H5("What Is the Lambert W Method for Calculating IV Curves?"),
        html.H6("The Lambert W method is a mathematical approach used to calculate IV curves. It is particularly useful when dealing with nonlinear curves and allows for precise determination of key parameters."),
        html.Hr()
        ])
    ])
# Define your app's "Contact" page layout
contact_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Markdown("# Contact")
        ], width=True),
    ], align="end"),
    html.Hr(),
    dbc.Row([
        html.Iframe(
            src='https://docs.google.com/forms/d/e/1FAIpQLSe9bizwPKrj5Oaeehhruycgtr7MFDlNSyT3vLJupQnv89QD4g/viewform?embedded=true',
            width='1000px',
            height='800px',
        )
    ]),
])

meta_description = "PV solar IV curve database and analysis tool. Explore performance data from thousands of modules like LONGi, Trina, Jinko, Canadian Solar, and more."
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

# IMPORT DATA INPUT
df_import = pd.DataFrame(columns=['Voltage', 'Current'], index=range(10))
import_input = dash_table.DataTable(
    id='import-input',
    columns=[{'name': col, 'id': col, 'type': 'numeric'} for col in df_import.columns],
    data=df_import.to_dict('records'),
    editable=True,
    style_table={'textAlign': 'center'},
    style_cell={'textAlign': 'center'},
    style_header={'textAlign': 'center'},
)



home_layout = dbc.Container(
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
                # ADD PARAMETERS
                dbc.Button("Add parameters", id="parameter_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(dropdown_parameters),
                    ),
                    id="parameter_collapse",
                    is_open=False
                ),
                html.Hr(),
                # DEGRADE
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
                # IMPORT YOUR DATA
                dbc.Button("Import your data", id="import_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([import_input]),
                    ),
                    id="import_collapse",
                    is_open=False
                ),
                html.Hr(),
                # ANALYZE YOUR DATA
                dbc.Button("Analyze your data", id="analyze_button"),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([  # Create DataTable for Pmp, Isc, Voc, Imp, Vmp
                                dbc.Col(dash_table.DataTable(
                                    id='my-parameters-table',
                                    columns=[{'name': col, 'id': col, 'type': 'numeric'} for col in ["Pmp", "Isc", "Voc", "Imp", "Vmp"]],
                                    data=[{}],
                                    style_table={'textAlign': 'center'},
                                    style_cell={'textAlign': 'center'},
                                    style_header={'textAlign': 'center'},
                                ), width=12),
                            ]),
                            ]),
                    ),
                    id="analyze_collapse",
                    is_open=False
                ),
            ], width=3),
            dbc.Col([
                dcc.Graph(id='display', style={'height': '80vh'}),
            ], width=9, align="start")
        ]),

        html.Hr(),

        dcc.Markdown("""
            © 2023 StreetPlant Solar. All Rights Reserved.
        """)

    ],
    fluid=True
)
                                                   
# Callbacks

# Define the callback to display the selected page
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/faq':
        return faq_layout
    if pathname == '/contact':
        return contact_layout
    else:
        return home_layout

def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

menus = ["module", "parameter", "degrade", "import", "analyze"]
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
    Output('my-parameters-table', 'data'),
    Input(import_input, 'data')
)
def update_my_parameters(data):
    if data:
        df_import = pd.DataFrame.from_dict(data)
        df_import['Power'] = df_import['Current'] * df_import['Voltage']

        if not df_import.empty:
            pmp = round(df_import['Power'].max(), 2)
            isc = round(df_import['Current'].max(), 2)
            voc = round(df_import['Voltage'].max(), 2)

            # Find the row where 'Power' is equal to the maximum power (Pmp)
            row_with_max_power = df_import[df_import['Power'] == df_import['Power'].max()]
            imp = round(row_with_max_power['Current'].values[0], 2)  # Get the 'Current' value from that row
            vmp = round(row_with_max_power['Voltage'].values[0], 2)
            data = [{'Pmp': pmp, 'Isc': isc, 'Voc': voc, 'Imp': imp, 'Vmp': vmp}]
            return data

    return [{}]

@app.callback(
    [
    Output("display", component_property='figure'),
    Output('module-parameters-table', 'data')
    ],
    [
        Input(dropdown_mod, 'value'),
        Input(dropdown_parameters, 'value'),
        Input(irradiance_input, 'value'),
        Input(temperature_input, 'value'),
        Input(string_input, 'value'),
        Input(degradation_date_picker, 'start_date'),
        Input(degradation_date_picker, 'end_date'),
        Input(degradation_input, 'value'),
        Input(import_input, 'data'),
    ]
)

def create_model_IV(selected_mod, selected_option, selected_irradiance, selected_temperature, mods_per_string, start_date, end_date, input_degradation_rate, data):
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
        ivcurve_pnts=150,
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

    df_import = pd.DataFrame.from_dict(data)

    fig.add_trace(
        go.Scatter(
            x=df_import['Voltage'],
            y=df_import['Current'],
            name="Your module",
            mode="lines",
            line_color="#ffce67",
            showlegend=False
        ),
        secondary_y=False
    )

    pmp = round(df_curve['Power'].max(), 2)
    isc = round(df_curve['Current'].max(), 2)
    voc = round(df_curve['Voltage'].max(), 2)

    # Find the row where 'Power' is equal to the maximum power (Pmp)
    df_mpp = df_curve[df_curve['Power'] == df_curve['Power'].max()]
    imp = round(df_mpp['Current'].values[0], 2)  # Get the 'Current' value from that row
    vmp = round(df_mpp['Voltage'].values[0], 2)
    data = [{'Pmp': pmp, 'Isc': isc, 'Voc': voc, 'Imp': imp, 'Vmp': vmp}]

    return fig, data

if __name__=='__main__':
    app.run_server(port=8053, debug=False)
