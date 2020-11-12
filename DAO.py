from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, BatchStatement
from cassandra.query import SimpleStatement
import pandas as pd
import numpy as np


class SensorsDAO:

    # Statements
    insert_stmt = None
    insert_stats_stmt = {}
    get_data_single_stmt = None
    get_data_single_stmt_spCol = None #specific columns
    get_data_range_stmt = None
    get_stats_stmt = {}
    get_sensor_status_stmt = None
    insert_sensor_status_stmt = None

    def __init__(self):
        self.cluster = None
        self.session = None
        self.keyspace = 'sensors'
        self.connection_status = False
        self.create_session()


    def __del__(self):
        self.cluster.shutdown()

    def create_session(self):
        try:
            self.cluster = Cluster(protocol_version=4)
            self.session = self.cluster.connect(self.keyspace)
            self.session.row_factory = pandas_factory
            self.session.default_fetch_size = None
            self.connection_status = True
            self.prepare_stmts()
        except:
            print("Connection refused!")
            self.connection_status = False
        
    def prepare_stmts(self):
        """
        Prepare CQL statements
        """
        SensorsDAO.insert_stmt = self.get_session().prepare(
            "INSERT INTO sensors_data (ip,name,date,datetime, temperature , relative_humidity , dew_point , co2_level ) values ( ?,?,?,?,?,?,?,?)")

        SensorsDAO.insert_stats_stmt = {
                "co2_level": self.get_session().prepare("INSERT INTO co2_level (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "dew_point": self.get_session().prepare("INSERT INTO dew_point (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "relative_humidity": self.get_session().prepare("INSERT INTO relative_humidity (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)"),
                "temperature": self.get_session().prepare("INSERT INTO temperature (date,ip,name,peak,mean,std ) values ( ?,?,?,?,?,?)") }

        SensorsDAO.get_data_single_stmt = self.get_session().prepare("select * from sensors_data where date = ?")

        SensorsDAO.get_data_single_stmt_spCol = self.get_session().prepare(
            "select ip,datetime,co2_level,dew_point,name,relative_humidity,temperature from sensors_data where date = ?")

        SensorsDAO.get_data_range_stmt = self.get_session().prepare(
            "select ip,datetime,co2_level,dew_point,name,relative_humidity,temperature from sensors_data where date >= ? AND date <= ? ALLOW FILTERING")
        
        SensorsDAO.get_stats_stmt = {
            "co2_level": "select * from sensors.co2_level",
            "dew_point": "select * from sensors.dew_point",
            "relative_humidity": "select * from sensors.relative_humidity",
            "temperature": "select * from sensors.temperature",
            }

        SensorsDAO.get_sensor_status_stmt = self.get_session().prepare("SELECT name, last_read, online FROM sensors_status")
        SensorsDAO.insert_sensor_status_stmt = self.get_session().prepare("INSERT INTO sensors_status (ip, name, last_read, online) VALUES (?,?,?,?)")

    def get_session(self):
        return self.session

    def get_data_single_spCol(self, date):
        """
        retreive data from single date with specific columns
        """
        try:
            if(self.connection_status == False):
                self.create_session()
            return self.get_session().execute(SensorsDAO.get_data_single_stmt_spCol, [date])._current_rows
        except:
            print("Data single spCol query failed!")
            return []

    def get_data_single(self, date):
        """
        retreive data from single date with specific columns
        """
        try:
            if(self.connection_status == False):
                self.create_session()
            return self.get_session().execute(SensorsDAO.get_data_single_stmt, [date])._current_rows
        except:
            print("Data single query failed!")
            return []
        
    def get_data_range(self, start_date, end_date):
        """
        retrieve data within date range
        """
        try:
            if(self.connection_status == False):
                self.create_session()
            return self.get_session().execute(SensorsDAO.get_data_range_stmt, [start_date,end_date])._current_rows
        except:
            print("Data range query failed!")
            return []

    def get_stats(self,source):
        """
        Get statistics data
        """
        try:
            if(self.connection_status == False):
                self.create_session()
            return self.get_session().execute(SensorsDAO.get_stats_stmt[source])._current_rows
        except:
            print("Statistics data query failed!")
            return []

    def insert_data(self,data):
        """
        Insert sensor data into DB
        """
        try:
            if(self.connection_status == False):
                self.create_session()
            self.get_session().execute(SensorsDAO.insert_stmt,data)
        except:
            print("Data Insertion failed!")

    def insert_stats(self,df):
        """
        Insert statistics data into DB
        """
        try:
            if(self.connection_status == False):
                self.create_session()

            for i in SensorsDAO.insert_stats_stmt:
                for key,grp in df.groupby(['ip','date','name']):
                    self.get_session().execute(SensorsDAO.insert_stats_stmt[i],[key[1],key[0],key[2],np.max(grp[i]),np.mean(grp[i]),np.std(grp[i]) ] )
        except:
            print("Stats data Insertion failed!")

    def get_sensor_status(self):
        """
        Get sensor status
        """
        try:
            return self.get_session().execute(SensorsDAO.get_sensor_status_stmt)._current_rows
        except:
            print("Sensors status data query failed!")
            return []

    def insert_sensor_status(self,data):
        """
        Insert Sensor status data into DB
        """
        try:
            if(self.connection_status == False):
                self.create_session()
            self.get_session().execute(SensorsDAO.insert_sensor_status_stmt,data ] )
        except:
            print("Sensor status data Insertion failed!")

def pandas_factory(colnames, rows):
        return pd.DataFrame(rows, columns=colnames)