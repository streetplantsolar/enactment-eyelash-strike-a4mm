import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import Dash, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


### Build the app
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], title="IVCurves.com")
server = app.server


###Module things
df_names = pd.read_excel('modules.xlsx')
df_voltage = pd.read_excel('modules.xlsx', sheet_name='Voltage')
df_current = pd.read_excel('modules.xlsx', sheet_name='Current')
dropdown_mods = dcc.Dropdown(options=df_names.iloc[:,0],
                        clearable=False)


###Parameter things
dropdown_parameters = dcc.Dropdown(options=['Pmp', 'Power Curve'],
                        clearable=True)


###Analyze things
dropdown_analyze = dcc.Dropdown(options=['Degrade', 'Scale'],
                        clearable=True)

df_IV=pd.DataFrame({            #initializes df as first mod
    'Voltage': df_voltage.iloc[:,0],
    'Current': df_current.iloc[:,0]
    })


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
                            dropdown_mods,
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
                            dropdown_analyze,
                        )
                    ),
                    id="analyze_collapse",
                    is_open=False
                ),
                html.Hr(),
            ], width=3),
            dbc.Col([
                dcc.Graph(id='display', style={'height': '90vh'}),
            ], width=9, align="start")
        ]),
    ],
    fluid=True
)

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


###############
#mygraph = dcc.Graph(figure={})

@app.callback(
    Output("display", component_property='figure'),
    Input(dropdown_mods, 'value'),
    Input(dropdown_parameters, 'value')
    #Input(dropdown_analyze, 'value')
)

def update_graph(selected_mod, selected_option):
    df=pd.DataFrame({            
        'Voltage': df_voltage.loc[:,str(selected_mod)],
        'Current': df_current.loc[:,str(selected_mod)]
        })
    #fig = px.line(df, x="Voltage", y="Current")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df.loc[:,"Voltage"],
            y=df.loc[:,"Current"],
            mode="lines",
            line_color="deepskyblue",
            showlegend=False)
        )
    fig.update_xaxes(title_text="Voltage")
    fig.update_yaxes(title_text="Current", secondary_y=False)
    df['Power'] = df['Voltage'] * df['Current']
    Pmp = df.loc[df['Power']==df['Power'].max()]
    
    if selected_option == "Power Curve":
        fig.add_trace(
            go.Scatter(
                x=df.loc[:,"Voltage"],
                y=df.loc[:,"Power"],
                mode="lines",
                line_color="goldenrod",
                showlegend=False),
            secondary_y=True
            )
        fig.update_yaxes(title_text="Power", secondary_y=True)
    
    if selected_option == "Pmp":
        fig.add_trace(
            go.Scatter(
                x=Pmp.loc[:,"Voltage"],
                y=Pmp.loc[:,"Current"],
                line_color="red",
                showlegend=False),
            secondary_y=False
            )
    return fig

if __name__=='__main__':
    app.run_server(port=8053)
