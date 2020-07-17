
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

## load sensors data
df = pd.read_csv('20200716_sensors.csv')

## replace not valid values with Zero
df['CO2 level'] = df['CO2 level'].replace(['connection'],'0')

app.layout = html.Div(children=[

    dcc.Graph(
        id='scatter',
        figure={
            'data': [
                go.Scatter(
                    x = df[(df.ip == "130_246_68_74")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_74")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.74"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_75")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_75")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.75"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_81")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_81")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.81"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_82")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_82")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.82"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_87")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_87")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.87"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_88")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_88")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.88"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_90")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_90")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.90"
                ),
                
                go.Scatter(
                    x = df[(df.ip == "130_246_68_91")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_91")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.91"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_92")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_92")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.92"
                ),
                go.Scatter(
                    x = df[(df.ip == "130_246_68_94")]['Time'].astype('datetime64[ns]'),
                    y= df[(df.ip == "130_246_68_94")]['CO2 level'],
                    mode = 'lines + markers',
                    name = "130.246.68.94"
                )
            ],
            'layout': go.Layout(
                title = 'Sensors CO2 Level',
                xaxis = {'title': 'Time'},
                yaxis = {'title': 'CO2'}
            )
        }
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)