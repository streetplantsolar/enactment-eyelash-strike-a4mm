import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd

df_names = pd.read_excel('modules.xlsx')
df_voltage = pd.read_excel('modules.xlsx', sheet_name='Voltage')
df_current = pd.read_excel('modules.xlsx', sheet_name='Current')


df_IV=pd.DataFrame({            #initializes df as first mod
    'Voltage': df_voltage.iloc[:,0],
    'Current': df_current.iloc[:,0]
    })


app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server
mytitle = dcc.Markdown(children="IV Curve Database & Calculator")
mygraph = dcc.Graph(figure={})
dropdown_mods = dcc.Dropdown(options=df_names.iloc[:,0],
                        clearable=False)
dropdown_options = dcc.Dropdown(options=['Pmp', 'Power Curve'],
                        clearable=True)

app.layout = dbc.Container([mytitle, mygraph, dropdown_mods, dropdown_options])

@app.callback(
    Output(mygraph, component_property='figure'),
    Input(dropdown_mods, 'value'),
    Input(dropdown_options, 'value')
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
    if selected_option == "Power Curve":
        df_pow = pd.DataFrame({
            'Voltage': df['Voltage'],
            'Power': df['Voltage'] * df['Current']
            })       
        fig.add_trace(
            go.Scatter(
                x=df_pow.loc[:,"Voltage"],
                y=df_pow.loc[:,"Power"],
                mode="lines",
                line_color="goldenrod",
                showlegend=False),
            secondary_y=True
            )
        fig.update_yaxes(title_text="Power", secondary_y=True)
    return fig

if __name__=='__main__':
    app.run_server(port=8053)
