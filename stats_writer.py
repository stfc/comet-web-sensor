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
        self._update_interval = update_interval
        self._cluster = Cluster()
        self._session = self._cluster.connect('sensors')
        self._session.row_factory = pandas_factory
        self._session.default_fetch_size = None

        self._insert_stmt = {
                "co2_level": self._session.prepare("INSERT INTO co2_level (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "dew_point": self._session.prepare("INSERT INTO dew_point (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "relative_humidity": self._session.prepare("INSERT INTO relative_humidity (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "temperature": self._session.prepare("INSERT INTO temperature (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)") }
        

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
        stmt_date_single = self._session.prepare("select * from sensors_data where date = ?")
        df = self._session.execute(stmt_date_single,[date])._current_rows
        print(df)
        return df

    def _write_dataframe_to_db(self,df):
        for i in self._insert_stmt:
            for key,grp in df.groupby(['ip','date','name']):
                self._session.execute(self._insert_stmt[i],[key[1],key[0],key[2],np.max(grp[i]),np.mean(grp[i]),np.std(grp[i]) ] )

    def start(self):
        while True:
            stats_data = self._process_stats_data()
            self._write_dataframe_to_db(stats_data)
            time.sleep(self._update_interval)


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


if __name__ == "__main__":
    test = StatsWriter()
    test.start()