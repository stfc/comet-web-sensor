
import dash, datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from flask import Flask
import numpy as np
from dash.dependencies import Input, Output


server = Flask(__name__)
app = dash.Dash(__name__, server = server)

def get_today():
    return datetime.date.today().strftime("%Y%m%d")

plot_refresh_time = 60 #seconds
data_source = '/opt/sensor_data/dash/' + get_today() + '_sensors.csv'

def get_and_condition_data(source):
    df = pd.read_csv(source)
    df = df.replace('connection',np.nan)
    df = df.replace('-',np.nan)
    df = df.astype({'Temperature':'float',
                    'Relative humidity':'float', 
                    'Dew point':'float', 
                    'CO2 level': 'float', 
                    'Time':'datetime64[ns]'})
    return df


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
    df = get_and_condition_data('/opt/sensor_data/dash/' + get_today() + '_sensors.csv')
    fig = go.Figure()
    for key, grp in df.groupby([sensor_tag]):
        fig.add_scatter(
            x=grp['Time'], 
            y=grp[parameter], 
            name=key, 
            mode='lines + markers',
            connectgaps=True)

    units = {'Temperature':'C', 'Relative humidity':'%', 'Dew point':'C', 'CO2 level': 'ppm'}
    fig.layout = {
        "yaxis": {
            "title": {"text":units[parameter]}
            }
        }
    return fig, parameter


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')