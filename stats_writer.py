import pandas as pd
from datetime import datetime as dt
from configparser import ConfigParser
import os, glob
from pathlib import Path
import numpy as np
import time
from cassandra.cluster import Cluster


class StatsWriter:
    def __init__(self, config_file="config.ini", update_interval=7200):
        self._read_config_file(config_file)
        self._measurement_files = {
            "Temperature": "Temp_stats.csv",
            "Relative humidity": "Humidity_stats.csv",
            "Dew point": "Dewpoint_stats.csv",
            "CO2 level": "CO2_stats.csv",
        }
        self._update_interval = update_interval

    def _read_config_file(self, config_file):
        cp = ConfigParser()
        cp.read(config_file)
        self._work_day_start = cp.get("settings", "work_day_start")
        self._work_day_end = cp.get("settings", "work_day_end")
        self._data_file_location = cp.get("settings", "data file location")

    def _get_available_files(self):
        return sorted(glob.glob(self._data_file_location + "/*_sensors.csv"))

    def _calc_stats(self, column, dataframe):
        stats = dataframe.groupby(["date", "ip", "name"], as_index=False).agg(
            {column: [np.max, np.mean, np.std]}
        )
        return stats


    def _process_stats_for_files(self, measurement):
        column_name = measurement
        filenames = self._get_available_files()
        stats_dataframe = pd.DataFrame()
        for filename in filenames:
            df = self._get_dataframe_from_file(filename, column_name)
            df = self._filter_dataframe_time_window(df)
            stats = self._calc_stats(column_name, df)
            stats_dataframe = stats_dataframe.append(stats)
        return stats_dataframe

    def _filter_dataframe_time_window(self, df):
        df = df.between_time(self._work_day_start, self._work_day_end).copy()
        df["date"] = df.index.strftime("%d/%m/%Y")
        return df

    def _get_dataframe_from_file(self, name, column):
        with open(name, "r") as f:
            df = pd.read_csv(
                f,
                usecols=["name", "ip", "Time", column],
                na_values=["connection", "-"],
                dtype={column: "float"},
                parse_dates=["Time"],
                infer_datetime_format=True,
                cache_dates=True,
                index_col="Time",
            )
        return df

    def _write_dataframe_to_file(self, stats_dataframe, filename):
        outfile = self._data_file_location + os.sep + filename
        first_line_in_file = "date,ip,name,peak,mean,std\n"
        with open(outfile, "w") as f:
            f.write(first_line_in_file)
            f.write(
                stats_dataframe.to_csv(header=False, index=False, line_terminator="\n")
            )

    def _write_dataframe_to_db(self,measurement,filename,session):
        readfile = self._data_file_location + os.sep + filename
        stmt = {"CO2 level": session.prepare("INSERT INTO co2_level (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "Dew point": session.prepare("INSERT INTO dew_point (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "Relative humidity": session.prepare("INSERT INTO relative_humidity (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "Temperature": session.prepare("INSERT INTO temperature (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)") }

        df = pd.read_csv(readfile, dtype={"peak": "float", "mean": "float", "std": "float"})
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

        for i in range(len(df)):
            
            ip = df.loc[i, "ip"]
            name = df.loc[i, "name"]
            date = df.loc[i, "date"]
            peak = df.loc[i, "peak"]
            std = df.loc[i, "std"]
            mean = df.loc[i, "mean"]
            
            session.execute(stmt[measurement], [date,ip,name,peak,mean,std])

    def start(self):
        cluster = Cluster()
        session = cluster.connect('sensors')
        while True:
            for measurement, filename in self._measurement_files.items():
                #stats_data = self._process_stats_for_files(measurement)
                #self._write_dataframe_to_file(stats_data, filename)
                self._write_dataframe_to_db(measurement,filename,session)
            time.sleep(self._update_interval)


if __name__ == "__main__":
    test = StatsWriter()
    test.start()

