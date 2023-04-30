import plotly.express as px
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
dropdown = dcc.Dropdown(options=df_names.iloc[:,0],
                        clearable=False)

app.layout = dbc.Container([mytitle, mygraph, dropdown])

@app.callback(
    Output(mygraph, component_property='figure'),
    Input(dropdown, component_property='value')
)

def update_graph(user_input):
    df=pd.DataFrame({            #initializes df as first mod
        'Voltage': df_voltage.loc[:,str(user_input)],
        'Current': df_current.loc[:,str(user_input)]
        })
    fig = px.line(df, x="Voltage", y="Current")
    return fig

if __name__=='__main__':
    app.run_server(port=8053)