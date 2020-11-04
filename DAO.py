from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, BatchStatement
from cassandra.query import SimpleStatement
import pandas as pd


class SensorsDAO:

    def __init__(self):
        self.cluster = None
        self.session = None
        self.keyspace = 'sensors'
        self.create_session()


    def __del__(self):
        self.cluster.shutdown()

    def create_session(self):
        self.cluster = Cluster()
        self.session = self.cluster.connect(self.keyspace)
        self.session.row_factory = pandas_factory
        self.session.default_fetch_size = None

    def get_session(self):
        return self.session

    def get_data_single(self, date):
        stmt_date_single = self.get_session().prepare(
        "select ip,datetime,co2_level,dew_point,name,relative_humidity,temperature from sensors_data where date = ?")

        return self.get_session().execute(stmt_date_single, [date])._current_rows
        
    def get_data_range(self, start_date, end_date):
        stmt_time_interval = self.get_session().prepare(
        "select ip,datetime,co2_level,dew_point,name,relative_humidity,temperature from sensors_data where date >= ? AND date <= ? ALLOW FILTERING")

        return self.get_session().execute(stmt_time_interval, [start_date,end_date])._current_rows

    def get_stats(self,source):
        stmt_list = {
        "co2_level": "select * from sensors.co2_level",
        "dew_point": "select * from sensors.dew_point",
        "relative_humidity": "select * from sensors.relative_humidity",
        "temperature": "select * from sensors.temperature",
        }

        return self.get_session().execute(stmt_list[source])._current_rows

def pandas_factory(colnames, rows):
        return pd.DataFrame(rows, columns=colnames)
