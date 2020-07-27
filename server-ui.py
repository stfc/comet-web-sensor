#!/usr/bin/env python3
import dash, datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from flask import Flask
import numpy as np
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

def get_today():
    return datetime.date.today().strftime("%Y%m%d")

plot_refresh_time = 20*60 #seconds

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
                            'width': '150px',
                            'height': '50%'
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
                            'width': '150px',
                            'height': '50%',
                            'mergin-left': '50px'
                            }
                    ),
                    width="auto"
            ),
            dbc.Col(children=
                    dcc.Dropdown(
                        id='data-resolution',
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
        ],style = {'padding-left': '100px',
                   'padding-top': '50px'}
    ),
    dcc.Graph(
            id='data-plot'
            ),

    html.Button('Refresh Now', id='refresh-btn', n_clicks=0),
    html.Button("Download", id="export_btn", n_clicks=0),
    Download(id="download"),
    dcc.ConfirmDialogProvider(
        children=html.Button(
            'Contact Us',
        ),
        id='contact-us',
        message='Please contact one of the following emails:\n\n- ahmad.alsabbagh@stfc.ac.uk\n- christopher.gregory@stfc.ac.uk'
    ),

    dcc.Interval(
        id='interval-component',
        interval=plot_refresh_time*1000, # in milliseconds
        n_intervals=0
    )
],
    style={"padding": "20px"}
)

@app.callback(
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
    [Output('data-plot', 'figure'),
    Output('plot-title', 'children')],
    [Input('parameter-picker', 'value'), 
    Input('legend-display-picker', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('my-date-picker-single', 'date'),
    Input('refresh-btn', 'n_clicks'),
    Input('data-resolution', 'value')]
    )
def update_output(parameter, sensor_tag, n_intervals,date,n_clicks,data_resolution):
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime("%Y%m%d")
        data_source =  '/opt/sensor_data/dash/'+date_string +'_sensors.csv'

    df = get_and_condition_data(data_source)
    fig = go.Figure()
    start_time = str(date) + " 06:00:00"
    df = df[df['Time'] > start_time]
    
    for key, grp in df.groupby([sensor_tag]):
        if(int(data_resolution) == 10):
            x_res=grp['Time'][::10]
            y_res=grp[parameter][::10]
        elif(int(data_resolution) == 1):
            x_res=grp['Time'][::1]
            y_res=grp[parameter][::1]
        else:
            x_res=grp['Time'][::5]
            y_res=grp[parameter][::5]

        fig.add_scatter(
            x= x_res, 
            y=y_res, 
            name=key, 
            mode='lines + markers',
            connectgaps=True)

    units = {'Temperature':'C', 'Relative humidity':'%', 'Dew point':'C', 'CO2 level': 'ppm'}
    fig.layout = {
        "yaxis": {
            "title": {"text":units[parameter]}
            },
            "uirevision":parameter
        }
    return fig, parameter


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')