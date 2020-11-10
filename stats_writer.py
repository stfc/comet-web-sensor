import pandas as pd
from datetime import datetime as dt
from configparser import ConfigParser
import os, glob
from pathlib import Path
import numpy as np
import time
from DAO import SensorsDAO


class StatsWriter:
    def __init__(self, config_file="config.ini", update_interval=7200):
        self._read_config_file(config_file)
        self._update_interval = update_interval
        self._db = SensorsDAO()

    def _read_config_file(self, config_file):
        cp = ConfigParser()
        cp.read(config_file)
        self._work_day_start = cp.get("settings", "work_day_start")
        self._work_day_end = cp.get("settings", "work_day_end")


    def _process_stats_data(self):
        df = self._get_dataframe_from_db(dt.now().date())
        df = self._filter_dataframe_time_window(df)
        
        return df

    def _filter_dataframe_time_window(self, df):
        df = df.set_index("datetime").between_time(self._work_day_start, self._work_day_end).reset_index()

        return df

    def _get_dataframe_from_db(self, date):
        return self._db.get_data_single(date)

    def start(self):
        while True:
            stats_data = self._process_stats_data()
            self._db.insert_stats(stats_data)
            time.sleep(self._update_interval)


if __name__ == "__main__":
    test = StatsWriter()
    test.start()