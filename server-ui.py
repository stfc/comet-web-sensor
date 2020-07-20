
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from flask import Flask
import numpy as np
from dash.dependencies import Input, Output


server = Flask(__name__)
app = dash.Dash(__name__, server = server)

def get_and_condition_data(source = './20200716/20200716_sensors.csv'):
    df = pd.read_csv(source)
    df = df.replace('connection','0')
    df = df.astype({'Temperature':'float', 'Relative humidity':'float', 'Dew point':'float', 'CO2 level': 'float', 'Time':'datetime64[ns]'})
    return df

df = get_and_condition_data()

app.layout = html.Div(children=[

    html.H1(id='plot-title'),

    dcc.Graph(
        id='data-plot'
    ),

    dcc.Dropdown(
        id='parameter-picker',
        options=[
            {'label': 'CO2 level', 'value': 'CO2 level'},
            {'label': 'Temperature', 'value': 'Temperature'},
            {'label': 'Dew point', 'value': 'Dew point'},
            {'label': 'Humidity', 'value': 'Relative humidity'}
        ],
        value='CO2 level'
    ),
])

@app.callback(
    [Output('data-plot', 'figure'),
    Output('plot-title', 'children')],
    [Input('parameter-picker', 'value')])
def update_output(value):

    fig = go.Figure()
    for key, grp in df.groupby(['ip']):
        fig.add_scatter(x=grp['Time'], y=grp[value], name=key, mode='lines + markers')
    return fig, value

if __name__ == '__main__':
    app.run_server(debug=True)