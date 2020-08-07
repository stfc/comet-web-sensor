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
import dash_table
import math

server = Flask(__name__)
app = dash.Dash(__name__, server = server,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                'https://codepen.io/chriddyp/pen/bWLwgP.css'])

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
            dbc.Col(children=[html.P('Data type',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
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
                    )],
            width="auto"
            ),
            dbc.Col(children=[html.P('Legend value',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
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
            dbc.Col(children=[html.P('Time interval',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
                    dcc.Dropdown(
                        id='data-time-interval',
                        options=[
                            {'label': '6:00 - 18:00', 'value': '06'},
                            {'label': '24 hours', 'value': '00'}
                        ],
                        value='06',
                        style={
                            'width': '150px',
                            'height': '50%',
                            'mergin-left': '50px'
                            }
                    )],
                    width="auto"
            ),
            dbc.Col(children=[html.P('Date',style={'font-size':'16px','font-weight': 'bold',"color": "#7c795d"}),
                    dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(2020, 7, 20),
                    max_date_allowed=datetime.date.today(),
                    date=datetime.date.today()
                    )],
                    width="auto"
            ),
            dbc.Col(html.Button('Refresh', id='refresh-btn', n_clicks=0,style={"padding": "0px", "width":"100px", "margin-top":"33px"}),
                    width="auto"
            ),
            dbc.Col(children=[html.Button("Export CSV", id="export_btn", n_clicks=0, style={"padding": "0px","width":"100px", "margin-top":"33px"}),Download(id="download")],
                    width = "auto"
            )
        ],
        style = {'padding-left': '100px',
                   'padding-top': '50px'}
    ),
    dcc.Graph(
            id='data-plot',
            style= {
                'height': 600
            }),
    dcc.Graph(
            id='average-plot',
            ),

    dash_table.DataTable(
    id='table',
    columns = [{"id": "name", "name": "Name"},
                {"id": "avg", "name": "Average"},
                {"id": "peak", "name": "Peak"},
                {"id": "rms", "name": "RMS"}],
    
    style_table = { "margin-left":"5%","width" : "45%"},
    style_cell={
        'text-align': 'left',
        'width': '150px'
    }),

    dcc.ConfirmDialogProvider(
        children=html.Button(
            'Contact Us',
            style={'bottom':'5%','margin-left':'20px', "margin-top":"20px" }
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
    [Output('my-date-picker-single', 'max_date_allowed'),
    Output('my-date-picker-single', 'date')],
    [Input('interval-component', 'n_intervals')],
    [State('my-date-picker-single', 'date')]
    )
def change(interval, date):
    if(dt.now().hour == 0):
        return datetime.date.today(), datetime.date.today()
    else:
        return datetime.date.today(), date

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

rms = lambda d: np.sqrt ((d ** 2) .sum ()/len(d))

@app.callback(
    [Output('data-plot', 'figure'),
    Output('plot-title', 'children'),
    Output('table', 'data'),
    Output('average-plot', 'figure')],
    [Input('parameter-picker', 'value'), 
    Input('legend-display-picker', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('my-date-picker-single', 'date'),
    Input('refresh-btn', 'n_clicks'),
    Input('sample-time-interval', 'value'),
    Input('data-time-interval', 'value')]
    )
def update_output(parameter, sensor_tag, n_intervals,date,n_clicks,sample_interval, data_interval):
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime("%Y%m%d")
        data_source =  '/opt/sensor_data/dash/'+date_string +'_sensors.csv'

    df = get_and_condition_data(data_source)
    fig = go.Figure()
    fig_avg = go.Figure()
    start_time = str(date) + " " + data_interval +":00:00"
    end_time = str(date) + " " + ("17" if int(data_interval) else "23" ) +":59:59"
    df = df[(df['Time'] > start_time) & (df['Time'] < end_time)]
    table_data = []
    for key, grp in df.groupby([sensor_tag]):
        sample_interval = int(sample_interval)

        fig.add_scatter(
            x= grp['Time'][::sample_interval], 
            y=grp[parameter][::sample_interval], 
            name=key, 
            mode='lines + markers',
            connectgaps=True)

    ## Filter according to working hours (8:00-16:00)
    ## Time interval to rectified with this range or add it as another option?
    start_time_w = str(date) + " 8:00:00"
    end_time_w = str(date) + " 16:00:00"
    dfw = get_and_condition_data('sum.csv')
    table_data = []

    for key, grp in dfw.groupby([sensor_tag]):

        fig_avg.add_scatter(
            x= grp['Time'], 
            y=grp[parameter], 
            name=key, 
            mode='lines + markers',
            connectgaps=True)

        if(math.isnan(grp[parameter].mean())):
            continue
        table_data.append({
            "name": key,
            "avg": "{:.2f}".format(grp[parameter].mean()),
            "peak": grp[parameter].max(),
            "rms": "{:.2f}".format(rms(grp[parameter]))
        })

    units = {'Temperature':'C', 'Relative humidity':'%', 'Dew point':'C', 'CO2 level': 'ppm'}
    fig.layout = {
        "yaxis": {
            "title": {"text":units[parameter]}
            },
            "uirevision":date
        }

    return fig, parameter, table_data, fig_avg


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')