
import dash, datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from flask import Flask
import numpy as np
from dash.dependencies import Input, Output
from datetime import datetime as dt
import dash_bootstrap_components as dbc
import re
import tkinter as tk
from tkinter import *
from tkinter import filedialog


server = Flask(__name__)
app = dash.Dash(__name__, server = server,external_stylesheets=[dbc.themes.BOOTSTRAP,'https://codepen.io/chriddyp/pen/bWLwgP.css'])

def get_today():
    return datetime.date.today().strftime("%Y%m%d")

plot_refresh_time = 20*60 #seconds
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
    dbc.Row(
        [
            dbc.Col(children=
                    dcc.Dropdown(
                        id='parameter-picker',
                        options=[
                            {'label': 'CO2 level', 'value': 'CO2 level'},
                            {'label': 'Temperature', 'value': 'Temperature'},
                            {'label': 'Dew point', 'value': 'Dew point'},
                            {'label': 'Humidity', 'value': 'Relative humidity'}
                        ],
                        value='CO2 level',
                        style={
                            'width': '200px',
                            'height': '50%',
                            }
                    ),
                    width="auto"
            ),
            dbc.Col(children=
                    dcc.Dropdown(
                        id='legend-display-picker',
                        options=[
                            {'label': 'IP address', 'value': 'ip'},
                            {'label': 'Name', 'value': 'name'}
                        ],
                        value='name',
                        style={
                            'width': '200px',
                            'height': '50%',
                            }
                    ),
                    width="auto"
            ),
            dbc.Col(children=
                    dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(2020, 7, 20),
                    max_date_allowed=datetime.date.today(),
                    date=datetime.date.today()
                    ),
                    width="auto"
            )
        ]
    ),
    dcc.Graph(
            id='data-plot'
            ),

    html.Button('Refresh Now', id='refresh-btn', n_clicks=0),
    html.Button('Save As', id='save-btn', n_clicks=0),
    html.Div(id='output-container-button'),
    

    dcc.Interval(
        id='interval-component',
        interval=plot_refresh_time*1000, # in milliseconds
        n_intervals=0
    )
],
    style={"padding": "20px"}
)

@app.callback(
    Output('output-container-button', 'children'),
    [Input('save-btn', 'n_clicks')]
    )
def export_csv(n_clicks):
    if n_clicks>0:
        global data_source
        df = get_and_condition_data(data_source)

        ## This will save into current directory
        ## To be chenged into user choosing
        df.to_csv("./data_exported",index=False)

@app.callback(
    [Output('data-plot', 'figure'),
    Output('plot-title', 'children')],
    [Input('parameter-picker', 'value'), 
    Input('legend-display-picker', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('my-date-picker-single', 'date'),
    Input('refresh-btn', 'n_clicks')]
    )
def update_output(parameter, sensor_tag, n_intervals,date,n_clicks):
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime("%Y%m%d")
        global data_source
        data_source =  '/opt/sensor_data/dash/'+date_string +'_sensors.csv'

    df = get_and_condition_data(data_source)
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