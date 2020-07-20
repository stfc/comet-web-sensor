
import dash, threading
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from flask import Flask
import numpy as np
from dash.dependencies import Input, Output


server = Flask(__name__)
app = dash.Dash(__name__, server = server)

plot_refresh_time = 20 #seconds
data_source = './dash/20200720_sensors.csv'

def get_and_condition_data(source = data_source):
    df = pd.read_csv(source)
    df = df.replace('connection','0')
    df = df.replace('-','0')
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

    dcc.Dropdown(
        id='legend-display-picker',
        options=[
            {'label': 'IP address', 'value': 'ip'},
            {'label': 'Name', 'value': 'name'}
        ],
        value='name'
    ),

    dcc.Interval(
        id='interval-component',
        interval=plot_refresh_time*1000, # in milliseconds
        n_intervals=0
        )


])

@app.callback(
    [Output('data-plot', 'figure'),
    Output('plot-title', 'children')],
    [Input('parameter-picker', 'value'), 
    Input('legend-display-picker', 'value'),
    Input('interval-component', 'n_intervals')]
    )
def update_output(parameter, sensor_tag, n_intervals):
    df = get_and_condition_data()
    fig = go.Figure()
    for key, grp in df.groupby([sensor_tag]):
        fig.add_scatter(x=grp['Time'], y=grp[parameter], name=key, mode='lines + markers')

    units = {'Temperature':'C', 'Relative humidity':'%', 'Dew point':'C', 'CO2 level': 'ppm'}
    fig.layout = {
        "yaxis": {
            "title": {"text":units[parameter]}
            }
        }
    return fig, parameter


if __name__ == '__main__':
    app.run_server(debug=True)