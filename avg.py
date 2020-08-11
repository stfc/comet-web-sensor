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
import csv

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

def calc_data():
    start = dt(2020, 7, 21).date()
    end = dt.today().date()
    csv_file = 'avg.csv'

    with open(csv_file, 'w') as f:
        f.write('ip,name,Time,Temperature,Relative humidity,Dew point,CO2 level\n')

        while start <= end:
            day = datetime.timedelta(days=1)
            date_string = start.strftime("%Y%m%d")
            data_source =  '/opt/sensor_data/dash/' + date_string +'_sensors.csv'

            start_time_w = str(start) + " 8:00:00"
            end_time_w = str(start) + " 16:00:00"
            
            df = get_and_condition_data(data_source)
            df = df[(df['Time'] > start_time_w) & (df['Time'] < end_time_w)]
        
            for key, grp in df.groupby(['name']):
                f.write("%s,%s,%s,%s,%s,%s,%s\n" 
                        %(grp['ip'].max(),
                        key,
                        start,
                        "{:.2f}".format(grp['Temperature'].mean()),
                        "{:.2f}".format(grp['Relative humidity'].mean()),
                        "{:.2f}".format(grp['Dew point'].mean()),
                        "{:.2f}".format(grp['CO2 level'].mean())))
            
            start += day

calc_data()