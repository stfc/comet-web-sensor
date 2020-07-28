#!/usr/bin/env python3
import dash, datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from flask import Flask
import numpy as np
<<<<<<< HEAD
from dash.dependencies import Input, Output
from datetime import datetime as dt
import dash_bootstrap_components as dbc
import re


server = Flask(__name__)
app = dash.Dash(__name__, server = server,external_stylesheets=[dbc.themes.BOOTSTRAP])

def get_today():
    return datetime.date.today().strftime("%Y%m%d")

plot_refresh_time = 60 #seconds
data_source = '/opt/sensor_data/dash/' + get_today() + '_sensors.csv'
=======
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import dash_bootstrap_components as dbc
import re
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import base64

server = Flask(__name__)
app = dash.Dash(__name__, server = server,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                'https://codepen.io/chriddyp/pen/bWLwgP.css'])

plot_refresh_time = 20*60 #seconds
>>>>>>> feature-data-resolution

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


<<<<<<< HEAD
app.layout = html.Div(children=[

    html.H1(id='plot-title'),
    dbc.Row(
        [
            dbc.Col(children=
=======
image_filename = 'CLFlogo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div(children=[

    dbc.Row([
        dbc.Col(children= html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),width='10%'),
        dbc.Col(children= html.H1(id='plot-title',
                style={"text-align": "center","font-family": "Trocchi","color": "#7c795d","width": "90%"}))
        ]),
    
    dbc.Row(
        [
            dbc.Col(children=[html.P('Data type',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
>>>>>>> feature-data-resolution
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
<<<<<<< HEAD
                            'width': '200px',
                            'height': '50%',
                            }
                    ),
                    width="auto"
            ),
            dbc.Col(children=
=======
                            'width': '150px',
                            'height': '50%'
                            }
                    )],
            width="auto"
            ),
            dbc.Col(children=[html.P('Legend value',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
>>>>>>> feature-data-resolution
                    dcc.Dropdown(
                        id='legend-display-picker',
                        options=[
                            {'label': 'IP address', 'value': 'ip'},
                            {'label': 'Name', 'value': 'name'}
                        ],
                        value='name',
                        style={
<<<<<<< HEAD
                            'width': '200px',
                            'height': '50%',
                            }
                    ),
                    width="auto"
            ),
            dbc.Col(children=
=======
                            'width': '150px',
                            'height': '50%',
                            'mergin-left': '50px'
                            }
                    )],
                    width="auto"
            ),
            dbc.Col(children=[html.P('Sample interval',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
                    dcc.Dropdown(
                        id='sample-time-interval',
                        options=[
                            {'label': '1 minute', 'value': '1'},
                            {'label': '5 minutes', 'value': '5'},
                            {'label': '10 minutes', 'value': '10'}
                        ],
                        value='5',
                        style={
                            'width': '150px',
                            'height': '50%',
                            'mergin-left': '50px'
                            }
                    )],
                    width="auto"
            ),
            dbc.Col(children=[html.P('Date',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
>>>>>>> feature-data-resolution
                    dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(2020, 7, 20),
                    max_date_allowed=datetime.date.today(),
                    date=datetime.date.today()
<<<<<<< HEAD
                    ),
                    width="auto"
            )
        ]
=======
                    )],
                    width="auto"
            )
        ],
        style = {'padding-left': '100px',
                   'padding-top': '50px'}
>>>>>>> feature-data-resolution
    ),
    dcc.Graph(
            id='data-plot'
            ),
<<<<<<< HEAD
    
=======

    html.Button('Refresh Now', id='refresh-btn', n_clicks=0, style={'margin-left':'20px' }),
    html.Button("Export CSV", id="export_btn", n_clicks=0, style={'margin-left':'20px' }),
    Download(id="download"),
    dcc.ConfirmDialogProvider(
        children=html.Button(
            'Contact Us',
            style={'position':'absolute','bottom':'5%','margin-left':'20px' }
        ),
        id='contact-us',
        message='Please contact one of the following emails:\n\n- ahmad.alsabbagh@stfc.ac.uk\n- christopher.gregory@stfc.ac.uk'
    ),
>>>>>>> feature-data-resolution

    dcc.Interval(
        id='interval-component',
        interval=plot_refresh_time*1000, # in milliseconds
        n_intervals=0
    )
],
    style={"padding": "20px"}
)

@app.callback(
<<<<<<< HEAD
=======
    Output("download", "data"),
    [Input("export_btn", "n_clicks")],
    [State('my-date-picker-single', 'date')]
    )
def export_csv(n_nlicks,date):
    if(n_nlicks>0):
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime("%Y%m%d")
        data_source = '/opt/sensor_data/dash/'+ date_string +'_sensors.csv'
        df = get_and_condition_data(data_source)

        return send_data_frame(df.to_csv, date_string+"_data.csv",index=False)

@app.callback(
>>>>>>> feature-data-resolution
    [Output('data-plot', 'figure'),
    Output('plot-title', 'children')],
    [Input('parameter-picker', 'value'), 
    Input('legend-display-picker', 'value'),
    Input('interval-component', 'n_intervals'),
<<<<<<< HEAD
    Input('my-date-picker-single', 'date')]
    )
def update_output(parameter, sensor_tag, n_intervals,date):
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime("%Y%m%d")
        global data_source
=======
    Input('my-date-picker-single', 'date'),
    Input('refresh-btn', 'n_clicks'),
    Input('sample-time-interval', 'value')]
    )
def update_output(parameter, sensor_tag, n_intervals,date,n_clicks,sample_interval):
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime("%Y%m%d")
>>>>>>> feature-data-resolution
        data_source =  '/opt/sensor_data/dash/'+date_string +'_sensors.csv'

    df = get_and_condition_data(data_source)
    fig = go.Figure()
<<<<<<< HEAD
    for key, grp in df.groupby([sensor_tag]):
        fig.add_scatter(
            x=grp['Time'], 
            y=grp[parameter], 
=======
    start_time = str(date) + " 06:00:00"
    df = df[df['Time'] > start_time]
    
    for key, grp in df.groupby([sensor_tag]):
        sample_interval = int(sample_interval)

        fig.add_scatter(
            x= grp['Time'][::sample_interval], 
            y=grp[parameter][::sample_interval], 
>>>>>>> feature-data-resolution
            name=key, 
            mode='lines + markers',
            connectgaps=True)

    units = {'Temperature':'C', 'Relative humidity':'%', 'Dew point':'C', 'CO2 level': 'ppm'}
    fig.layout = {
        "yaxis": {
            "title": {"text":units[parameter]}
<<<<<<< HEAD
            }
=======
            },
            "uirevision":parameter
>>>>>>> feature-data-resolution
        }
    return fig, parameter


if __name__ == '__main__':
<<<<<<< HEAD
    app.run_server(debug=True, host='0.0.0.0')
=======
    app.run_server(debug=True, host='0.0.0.0')
>>>>>>> feature-data-resolution
