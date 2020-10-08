#!/usr/bin/env python3
import dash, datetime, os, time
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from flask import Flask
import numpy as np
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import dash_bootstrap_components as dbc
import re
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from plotly.subplots import make_subplots
import base64
import dash_table
import math
from configparser import ConfigParser
import dash_daq as daq
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.query import dict_factory


server = Flask(__name__)

cluster = Cluster()
session = cluster.connect("sensors")


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


session.row_factory = pandas_factory
session.default_fetch_size = None

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
    ],
)

image_filename = "CLFlogo.png"
encoded_image = base64.b64encode(open(image_filename, "rb").read())

cp = ConfigParser()
cp.read("config.ini")
plot_refresh_time = cp.getfloat("settings", "plot refresh interval")
data_file_location = cp.get("settings", "data file location")
work_day_start = cp.get("settings", "work_day_start")
work_day_end = cp.get("settings", "work_day_end")

stats_file_dict = {
    "temperature": "Temp_stats.csv",
    "relative_humidity": "Humidity_stats.csv",
    "dew_point": "Dewpoint_stats.csv",
    "co2_level": "CO2_stats.csv",
}
units = {
    "temperature": "C",
    "relative_humidity": "%",
    "dew_point": "C",
    "co2_level": "ppm",
}


app.layout = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    children=html.Img(
                        src="data:image/png;base64,{}".format(encoded_image.decode())
                    ),
                    width="10%",
                ),
                dbc.Col(
                    children=[
                        html.H1(
                            "THIS IS DEVELOPMENT BRANCH IT CAN BE SWITCHED OFF ANYTIME",
                            style={
                                "text-align": "left",
                                "font-family": "Trocchi",
                                "color": "red",
                                "width": "50%",
                                "font-size": "20px",
                            },
                        ),
                        html.Label(
                            [
                                "FOR STABLE VERSION\t",
                                html.A("CLICK HERE", href="http://130.246.71.15:8050"),
                            ],
                            style={
                                "text-align": "left",
                                "font-family": "Trocchi",
                                "color": "red",
                                "width": "50%",
                                "font-size": "20px",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    children=html.H1(
                        id="plot-title",
                        style={
                            "font-family": "Trocchi",
                            "color": "#7c795d",
                            "width": "60%",
                            "margin-left": "-20%",
                        },
                    )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        html.P(
                            "Data type",
                            style={
                                "font-size": "16px",
                                "font-weight": "bold",
                                "color": "#7c795d",
                            },
                        ),
                        dcc.Dropdown(
                            id="parameter-picker",
                            options=[
                                {"label": "CO2 level", "value": "co2_level"},
                                {"label": "Temperature", "value": "temperature"},
                                {"label": "Dew point", "value": "dew_point"},
                                {"label": "Humidity", "value": "relative_humidity"},
                            ],
                            value="co2_level",
                            style={"width": "150px", "height": "50%"},
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    children=[
                        html.P(
                            "Legend value",
                            style={
                                "font-size": "16px",
                                "font-weight": "bold",
                                "color": "#7c795d",
                            },
                        ),
                        dcc.Dropdown(
                            id="legend-display-picker",
                            options=[
                                {"label": "IP address", "value": "ip"},
                                {"label": "Name", "value": "name"},
                            ],
                            value="name",
                            style={
                                "width": "150px",
                                "height": "50%",
                                "mergin-left": "50px",
                            },
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    id="sensors-alive", width="auto", style={"margin-top": "27px",}
                ),
            ],
            style={
                "padding-left": "100px",
                "padding-top": "50px",
                "margin-bottom": "50px",
            },
        ),
        dcc.Loading(
            id="loading-spin",
            type="circle",
            children=[
                dcc.Tabs(
                    children=[
                        dcc.Tab(
                            label="Daily",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Sample interval",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="sample-time-interval",
                                                    options=[
                                                        {
                                                            "label": "1 minute",
                                                            "value": "1",
                                                        },
                                                        {
                                                            "label": "5 minutes",
                                                            "value": "5",
                                                        },
                                                        {
                                                            "label": "10 minutes",
                                                            "value": "10",
                                                        },
                                                    ],
                                                    value="5",
                                                    style={
                                                        "width": "150px",
                                                        "height": "50%",
                                                        "mergin-left": "50px",
                                                    },
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Time interval",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="data-time-interval",
                                                    options=[
                                                        {
                                                            "label": "24 hours",
                                                            "value": "00:00:00,23:59:00",
                                                        },
                                                        {
                                                            "label": "6:00 - 18:00",
                                                            "value": "06:00:00,18:00:00",
                                                        },
                                                    ],
                                                    value="00:00:00,23:59:00",
                                                    style={
                                                        "width": "150px",
                                                        "height": "50%",
                                                        "mergin-left": "50px",
                                                    },
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Date",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.DatePickerSingle(
                                                    id="date-picker",
                                                    min_date_allowed=dt(2020, 7, 20),
                                                    max_date_allowed=datetime.date.today(),
                                                    date=datetime.date.today(),
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            html.Button(
                                                "Refresh",
                                                id="refresh-btn",
                                                n_clicks=0,
                                                style={
                                                    "padding": "0px",
                                                    "width": "100px",
                                                    "margin-top": "33px",
                                                },
                                            ),
                                            width="auto",
                                        ),
                                    ],
                                    style={
                                        "padding-left": "100px",
                                        "padding-top": "20px",
                                    },
                                ),
                                dcc.Graph(id="data-plot", style={"height": 600}),
                                html.Button(
                                    "Export Data",
                                    id="export_btn",
                                    n_clicks=0,
                                    style={
                                        "padding": "0px",
                                        "width": "100px",
                                        "margin-top": "33px",
                                        "margin-bottom": "20px",
                                    },
                                ),
                                Download(id="download"),
                                dash_table.DataTable(
                                    id="table",
                                    columns=[
                                        {"id": "name", "name": "Name"},
                                        {"id": "peak", "name": "Peak"},
                                        {"id": "avg", "name": "Average"},
                                        {"id": "std", "name": "Std"},
                                    ],
                                    style_table={"margin-left": "5%", "width": "45%"},
                                    style_cell={"text-align": "left", "width": "150px"},
                                ),
                                html.Div(
                                    id="plot-intermediate-value",
                                    style={"display": "none"},
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="Statistics",
                            children=[
                                dcc.Graph(id="stats-plot", style={"height": 900}),
                                html.Button(
                                    "Export Data",
                                    id="export_stats-btn",
                                    n_clicks=0,
                                    style={
                                        "padding": "0px",
                                        "margin-left": "20px",
                                        "width": "140px",
                                        "margin-top": "33px",
                                        "margin-bottom": "20px",
                                    },
                                ),
                                Download(id="download-stats"),
                            ],
                        ),
                        dcc.Tab(
                            label="Sensors Status",
                            children=[
                                dash_table.DataTable(
                                    id="table-alive",
                                    columns=[
                                        {"id": "name", "name": "Name"},
                                        {"id": "timestamp", "name": "Timestamp"},
                                        {"id": "timeout", "name": "timeout"},
                                    ],
                                    style_table={
                                        "margin-left": "5%",
                                        "width": "20%",
                                        "margin-top": "20px",
                                    },
                                    style_cell={"text-align": "left"},
                                    hidden_columns=["timeout"],
                                    css=[
                                        {
                                            "selector": ".show-hide",
                                            "rule": "display: none",
                                        }
                                    ],
                                    style_data_conditional=[
                                        {
                                            "if": {
                                                "filter_query": '{timeout} eq "valid"',
                                                "column_id": "timestamp",
                                            },
                                            "backgroundColor": "#98ff98",
                                        },
                                        {
                                            "if": {
                                                "filter_query": '{timeout} eq "invalid"',
                                                "column_id": "timestamp",
                                            },
                                            "backgroundColor": "#ff4040",
                                        },
                                    ],
                                )
                            ],
                        ),
                        dcc.Tab(
                            label="Historical Range",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Sample interval",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="sample-time-interval-range",
                                                    options=[
                                                        {
                                                            "label": "1 minute",
                                                            "value": "1",
                                                        },
                                                        {
                                                            "label": "5 minutes",
                                                            "value": "5",
                                                        },
                                                        {
                                                            "label": "10 minutes",
                                                            "value": "10",
                                                        },
                                                    ],
                                                    value="5",
                                                    style={
                                                        "width": "150px",
                                                        "height": "50%",
                                                        "mergin-left": "50px",
                                                    },
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Date",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.DatePickerRange(
                                                    id="date-picker-range",
                                                    min_date_allowed=dt(2020, 7, 20),
                                                    max_date_allowed=datetime.date.today(),
                                                    start_date=datetime.date.today(),
                                                    end_date=datetime.date.today(),
                                                    show_outside_days=True,
                                                    minimum_nights=0,
                                                    clearable=True,
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                    ],
                                    style={
                                        "padding-left": "100px",
                                        "padding-top": "20px",
                                    },
                                ),
                                dcc.Graph(id="data-plot-range", style={"height": 600}),
                                html.Button(
                                    "Export Data",
                                    id="export_btn-range",
                                    n_clicks=0,
                                    style={
                                        "padding": "0px",
                                        "width": "100px",
                                        "margin-top": "33px",
                                        "margin-bottom": "20px",
                                    },
                                ),
                                Download(id="download-range"),
                                html.Div(
                                    id="plot-intermediate-value-range",
                                    style={"display": "none"},
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="Temp vs. CO2",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Sample interval",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="data-interval-T-vs-CO2",
                                                    options=[
                                                        {
                                                            "label": "1 minute",
                                                            "value": "1",
                                                        },
                                                        {
                                                            "label": "5 minutes",
                                                            "value": "5",
                                                        },
                                                        {
                                                            "label": "10 minutes",
                                                            "value": "10",
                                                        },
                                                    ],
                                                    value="5",
                                                    style={
                                                        "width": "150px",
                                                        "height": "50%",
                                                        "mergin-left": "50px",
                                                    },
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            children=[
                                                html.P(
                                                    "Date",
                                                    style={
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                        "color": "#7c795d",
                                                    },
                                                ),
                                                dcc.DatePickerRange(
                                                    id="date-range-T-vs-CO2",
                                                    min_date_allowed=dt(2020, 7, 20),
                                                    max_date_allowed=datetime.date.today(),
                                                    start_date=datetime.date.today(),
                                                    end_date=datetime.date.today(),
                                                    show_outside_days=True,
                                                    minimum_nights=0,
                                                    clearable=True,
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                    ],
                                    style={
                                        "padding-left": "100px",
                                        "padding-top": "20px",
                                    },
                                ),
                                dcc.Graph(
                                    id="data-plot-T-vs-CO2", style={"height": 600}
                                ),
                                html.Button(
                                    "Export Data",
                                    id="export_btn-TempVsCO2",
                                    n_clicks=0,
                                    style={
                                        "padding": "0px",
                                        "width": "100px",
                                        "margin-top": "33px",
                                        "margin-bottom": "20px",
                                    },
                                ),
                                Download(id="download-TempVsCO2"),
                                html.Div(
                                    id="plot-intermediate-TempVsCO2",
                                    style={"display": "none"},
                                ),
                            ],
                        ),
                    ]
                ),
            ],
        ),
        dcc.ConfirmDialogProvider(
            children=html.Button(
                "Contact Us",
                style={"bottom": "5%", "margin-left": "20px", "margin-top": "20px"},
            ),
            id="contact-us",
            message="Please contact one of the following emails:\n\n- ahmad.alsabbagh@stfc.ac.uk\n- christopher.gregory@stfc.ac.uk",
        ),
        dcc.Interval(
            id="interval-component",
            interval=plot_refresh_time * 1000,  # in milliseconds
            n_intervals=0,
        ),
    ],
    style={"padding": "20px"},
)


@app.callback(
    Output("date-picker", "max_date_allowed"),
    [Input("interval-component", "n_intervals")],
)
def update_max_date(n_invervals):
    return datetime.date.today()


@app.callback(
    Output("date-picker", "date"), [Input("interval-component", "n_intervals")]
)
def update_current_date(n_intervals):
    if n_intervals == 0:
        return datetime.date.today()
    else:
        return dash.no_update


@app.callback(
    Output("download-TempVsCO2", "data"),
    [Input("export_btn-TempVsCO2", "n_clicks")],
    [
        State("date-range-T-vs-CO2", "start_date"),
        State("date-range-T-vs-CO2", "end_date"),
        State("data-plot-T-vs-CO2", "figure"),
        State("legend-display-picker", "value"),
        State("plot-intermediate-TempVsCO2", "children"),
    ],
)
def export_TempVsCO2_csv(n_clicks, start_date, end_date, plot, sensor_tag, df_save):
    if n_clicks > 0:
        out_filename = str(start_date) + "_" + str(end_date) + "_data.csv"
        df = pd.read_json(df_save, orient="split")

        visible_traces = []
        for key in plot["data"]:
            if key.get("visible") == 1 or str(key.get("visible")) == "None":
                visible_traces.append(key.get(sensor_tag))
        df = df[df[sensor_tag].isin(visible_traces)]

        return send_data_frame(
            df.sort_values(by=["ip", "datetime"]).to_csv, out_filename, index=False
        )

@app.callback(
    Output("download-range", "data"),
    [Input("export_btn-range", "n_clicks")],
    [
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("data-plot-range", "figure"),
        State("legend-display-picker", "value"),
        State("plot-intermediate-value-range", "children"),
    ],
)
def export_range_csv(n_clicks, start_date, end_date, plot, sensor_tag, df_save):
    if n_clicks > 0:
        out_filename = str(start_date) + "_" + str(end_date) + "_data.csv"
        df = pd.read_json(df_save, orient="split")

        visible_traces = []
        for key in plot["data"]:
            if key.get("visible") == 1 or str(key.get("visible")) == "None":
                visible_traces.append(key.get(sensor_tag))
        df = df[df[sensor_tag].isin(visible_traces)]

        return send_data_frame(
            df.sort_values(by=["ip", "datetime"]).to_csv, out_filename, index=False
        )


@app.callback(
    Output("download", "data"),
    [Input("export_btn", "n_clicks")],
    [
        State("date-picker", "date"),
        State("data-plot", "figure"),
        State("legend-display-picker", "value"),
        State("plot-intermediate-value", "children"),
    ],
)
def export_csv(n_clicks, date, plot, sensor_tag, df_save):
    if n_clicks > 0:
        data_source = get_sensor_datafile_name(date)
        df = pd.read_json(df_save, orient="split")
        out_filename = data_source.split("_")[0] + "_data.csv"

        visible_traces = []
        for key in plot["data"]:
            if key.get("visible") == 1 or str(key.get("visible")) == "None":
                visible_traces.append(key.get(sensor_tag))
        df = df[df[sensor_tag].isin(visible_traces)]

        return send_data_frame(
            df.sort_values(by=["ip", "datetime"]).to_csv, out_filename, index=False
        )
    return dash.no_update


@app.callback(
    Output("download-stats", "data"),
    [Input("export_stats-btn", "n_clicks")],
    [State("date-picker", "date"), State("parameter-picker", "value")],
)
def export_stats(n_clicks, date, parameter):
    if n_clicks > 0:
        stats_file = stats_file_dict[parameter]
        df_stats = get_and_condition_stats(stats_file)
        return send_data_frame(df_stats.to_csv, stats_file, index=False)


@app.callback(
    [
        Output("data-plot-T-vs-CO2", "figure"),
        Output("plot-intermediate-TempVsCO2", "children")
    ],
    [
        Input("date-range-T-vs-CO2", "end_date"),
        Input("sample-time-interval-range", "value"),
        Input("legend-display-picker", "value"),
    ],
    [State("date-range-T-vs-CO2", "start_date")],
)
def update_temp_co2_graph(end_date, sample_interval, sensor_tag, start_date):
    fig = go.Figure()
    try:
        df_range = get_and_condition_data(start_date, start_date, end_date)
    except FileNotFoundError:
        # TODO let user know data doesn't exist for this date
        return []

    sample_interval = int(sample_interval)
    symbols_shape = ["circle", "diamond-open", "triangle-up","circle-open"]
    count_set = shape_index = 0

    for key, grp in df_range.groupby([sensor_tag]):
        fig.add_scattergl(
            x=grp["temperature"][::sample_interval],
            y=grp["co2_level"][::sample_interval],
            name=key,
            mode="markers",
            connectgaps=False,
            marker_symbol=symbols_shape[shape_index],
        )
        count_set += 1
        if count_set % len(px.colors.qualitative.Plotly) == 0:
            shape_index = (shape_index + 1) % len(symbols_shape)

    fig.update_layout(
        {"yaxis": {"title": {"text": "ppm"}}}, {"xaxis": {"title": {"text": "C"}}}
    )

    df_save = df_range.to_json(date_format="iso", orient="split")

    return fig, df_save


@app.callback(
    [
        Output("data-plot", "figure"),
        Output("plot-title", "children"),
        Output("table", "data"),
        Output("stats-plot", "figure"),
        Output("table-alive", "data"),
        Output("sensors-alive", "children"),
        Output("plot-intermediate-value", "children"),
    ],
    [
        Input("parameter-picker", "value"),
        Input("legend-display-picker", "value"),
        Input("interval-component", "n_intervals"),
        Input("date-picker", "date"),
        Input("refresh-btn", "n_clicks"),
        Input("sample-time-interval", "value"),
        Input("data-time-interval", "value"),
    ],
)
def update_output(
    parameter, sensor_tag, n_intervals, date, n_clicks, sample_interval, data_interval
):

    fig_main = go.Figure()
    fig_stats = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=["Peak", "Mean", "STD"],
        vertical_spacing=0.05,
    )

    try:
        df = get_and_condition_data(date)
    except FileNotFoundError:
        # TODO let user know that data for that day doesn't exist.
        return fig_main, parameter, [], fig_stats

    df_time_filt = get_data_in_time_interval(data_interval, df)

    line_shape = ["solid", "dash", "dot", "dashdot", "longdash"]
    count_set = 0
    shape_index = 0
    sample_interval = int(sample_interval)

    for key, grp in df_time_filt.groupby([sensor_tag]):
        fig_main.add_scattergl(
            x=grp["datetime"][::sample_interval],
            y=grp[parameter][::sample_interval],
            name=key,
            mode="lines + markers",
            connectgaps=True,
            line=dict(dash=line_shape[shape_index]),
        )
        count_set += 1
        if count_set % len(px.colors.qualitative.Plotly) == 0:
            shape_index = (shape_index + 1) % len(line_shape)

    table_data = build_table(df, sensor_tag, parameter)

    df_stats = get_and_condition_stats(parameter)

    count_set = shape_index = 0

    for key, grp in df_stats.groupby([sensor_tag]):

        fig_stats.add_trace(
            make_scatter(
                grp["date"].astype(str), grp["peak"], key, line_shape[shape_index], True
            ),
            row=1,
            col=1,
        )

        fig_stats.add_trace(
            make_scatter(
                grp["date"].astype(str),
                grp["mean"],
                key,
                line_shape[shape_index],
                False,
            ),
            row=2,
            col=1,
        )

        fig_stats.add_trace(
            make_scatter(
                grp["date"].astype(str), grp["std"], key, line_shape[shape_index], False
            ),
            row=3,
            col=1,
        )

        count_set += 1
        if count_set % len(px.colors.qualitative.Plotly) == 0:
            shape_index = (shape_index + 1) % len(line_shape)

    for f in [fig_main, fig_stats]:
        f.update_layout(
            {"yaxis": {"title": {"text": units[parameter]}}, "uirevision": date}
        )

    table_sensors_alive = build_sensors_status()
    sensors_alive = get_sensors_status()

    df_save = df_time_filt.to_json(date_format="iso", orient="split")

    return (
        fig_main,
        parameter,
        table_data,
        fig_stats,
        table_sensors_alive,
        sensors_alive,
        df_save,
    )


@app.callback(
    [
        Output("data-plot-range", "figure"),
        Output("plot-intermediate-value-range", "children"),
    ],
    [
        Input("parameter-picker", "value"),
        Input("legend-display-picker", "value"),
        Input("date-picker-range", "end_date"),
        Input("sample-time-interval-range", "value"),
    ],
    [State("date-picker-range", "start_date")],
)
def update_output_dateRange(
    parameter, sensor_tag, end_date, sample_interval, start_date
):

    fig_range = go.Figure()

    try:
        df_range = get_and_condition_data(start_date, start_date, end_date)
        df_range = df_range.sort_values(by=["datetime"])
    except FileNotFoundError:
        # TODO let user know that data for that day doesn't exist.
        return []

    line_shape = ["solid", "dash", "dot", "dashdot", "longdash"]
    count_set = 0
    shape_index = 0
    sample_interval = int(sample_interval)

    for key, grp in df_range.groupby([sensor_tag]):
        fig_range.add_scattergl(
            x=grp["datetime"][::sample_interval],
            y=grp[parameter][::sample_interval],
            name=key,
            mode="lines + markers",
            connectgaps=True,
            line=dict(dash=line_shape[shape_index]),
        )
        count_set += 1
        if count_set % len(px.colors.qualitative.Plotly) == 0:
            shape_index = (shape_index + 1) % len(line_shape)

    fig_range.update_layout({"yaxis": {"title": {"text": units[parameter]}}})

    df_save = df_range.to_json(date_format="iso", orient="split")

    return fig_range, df_save


def get_sensors_status():
    sensors_csv = data_file_location + "/sensors_status.csv"
    sensors_status = pd.read_csv(sensors_csv)
    led_color = "green"
    name = "Sensors Connected"

    for i in range(len(sensors_status)):
        if sensors_status.loc[i, "timeout"] == "invalid":
            led_color = "red"
            name = "Some Sensors Disconnected"

    led = daq.Indicator(labelPosition="bottom", color=led_color, label=name)

    return led


def make_scatter(x_vals, y_vals, key, line_shape, leg):
    return go.Scatter(
        x=x_vals,
        y=y_vals,
        name=key,
        mode="lines + markers",
        connectgaps=False,
        legendgroup=key,
        showlegend=leg,
        line=dict(dash=line_shape),
    )


def setup_graph_title(title_string):
    return {
        "text": title_string,
        "y": 0.9,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }


def get_data_in_time_interval(data_interval, df):
    start_time, end_time = data_interval.split(",")
    df = df.set_index("datetime").between_time(start_time, end_time).reset_index()
    return df


def build_table(df, sensor_tag, parameter):
    df = df.set_index("datetime")
    table_data = []
    for key, grp in df.groupby([sensor_tag]):
        if math.isnan(grp[parameter].mean()):
            continue
        table_data.append(
            {
                "name": key,
                "peak": grp[parameter].max(),
                "avg": "{:.2f}".format(grp[parameter].mean()),
                "std": "{:.2f}".format(np.std(grp[parameter])),
            }
        )
    return table_data


def build_sensors_status():
    sensors_csv = data_file_location + "/sensors_status.csv"
    sensors_status = pd.read_csv(sensors_csv)
    table_data_alive = []
    for i in range(len(sensors_status)):
        table_data_alive.append(
            {
                "name": sensors_status.loc[i, "name"],
                "timestamp": sensors_status.loc[i, "timestamp"],
                "timeout": sensors_status.loc[i, "timeout"],
            }
        )

    return table_data_alive


def get_and_condition_data(date, start_date="", end_date=""):
    """
    Query sensors data on with specified date/date range
    """
    stmt_time_interval = session.prepare(
        "select ip,datetime,co2_level,dew_point,name,relative_humidity,temperature from sensors_data where date >= ? AND date <= ? ALLOW FILTERING"
    )
    stmt_date_single = session.prepare(
        "select ip,datetime,co2_level,dew_point,name,relative_humidity,temperature from sensors_data where date = ?"
    )

    if start_date == end_date:
        df = session.execute(stmt_date_single, [date])._current_rows

    else:
        df = session.execute(stmt_time_interval, [start_date, end_date])._current_rows

    return df


def get_and_condition_stats(source):

    stmt_list = {
        "co2_level": "select * from sensors.co2_level",
        "dew_point": "select * from sensors.dew_point",
        "relative_humidity": "select * from sensors.relative_humidity",
        "temperature": "select * from sensors.temperature",
    }

    df = session.execute(stmt_list[source])._current_rows
    return df


def get_sensor_datafile_name(date):
    date = dt.strptime(re.split("T| ", date)[0], "%Y-%m-%d")
    date_string = date.strftime("%Y%m%d")
    return data_file_location + os.sep + date_string + "_sensors.csv"


if __name__ == "__main__":
    app.run_server(port=8051, debug=True, host="0.0.0.0")

