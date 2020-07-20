
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
df = pd.read_csv('./20200716/20200716_sensors.csv')

## replace not valid values with Zero
df = df.replace('connection','0')
df = df.astype({'Temperature':'float', 'Relative humidity':'float', 'Dew point':'float', 'CO2 level': 'float', 'Time':'datetime64[ns]'})


fig = go.Figure()
for key, grp in df.groupby(['ip']):
    fig.add_scatter(x=grp['Time'], y=grp['Temperature'], name=key, mode='lines + markers')


app.layout = html.Div(children=[

    dcc.Graph(
        id='scatter',
        figure=fig
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)