import os, datetime, time
from configparser import ConfigParser
from pathlib import Path
from sensor import Sensor
import smtplib, ssl
from email.message import EmailMessage
import sys
from cassandra.cluster import Cluster
from DAO import SensorsDAO

if(float(sys.version[:3])<3.7):
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()


class SensorDataReader:
    def __init__(self, config_file="config.ini"):
        self._read_config_file(config_file)
        self._sensors = [Sensor(d) for d in self._sensors_details]

    def _read_config_file(self, config_file):
        cp = ConfigParser()
        cp.read(config_file)
        self._sensors_details = [
            {"ip": i[0], "name": i[1]} for i in cp["sensors"].items()
        ]
        self._sample_interval = cp.getint("settings", "sensor read interval")
        self._data_file_location = cp.get("settings", "data file location")
        self._timeout_value = cp.getint("settings", "warning timeout")

    def _get_today(self):
        return datetime.date.today().strftime("%Y%m%d")

    def _make_dir_if_needed(self, filename):
        directory, _ = os.path.split(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _generate_todays_filename(self):
        return self._data_file_location + os.sep + self._get_today() + "_sensors.csv"

    def _make_todays_csv_file_if_necessary(self):
        filename = self._generate_todays_filename()
        if not Path(filename).is_file():
            first_line_in_file = (
                "ip,name,Time,Temperature,Relative humidity,Dew point,CO2 level\n"
            )
            self._make_dir_if_needed(filename)
            with open(filename, "w") as f:
                f.write(first_line_in_file)
        return filename

    def _start_sensors(self):
        for sensor in self._sensors:
            sensor.start_data_collection(self._sample_interval)

    def _check_sensor_status(self):
        sensors_status = self._data_file_location + os.sep + "sensors_status.csv"
        first_line_in_file = "name,timestamp,timeout\n"

        with open(sensors_status, "w") as f:
            f.write(first_line_in_file)
            for s in self._sensors:
                if s.seconds_since_successful_read > self._timeout_value:
                    f.write(s.name+","+str(s.time_of_last_successful_read)+","+"invalid\n")
                else:
                    f.write(s.name+","+str(s.time_of_last_successful_read)+","+"valid\n")

    def db_connect(self):
        cluster = Cluster()
        session = cluster.connect('sensors')
        return session

    def get_insert_stmt(self,session):
        return session.prepare("INSERT INTO sensors_data (ip,name,date,time, temperature , relative_humidity , dew_point , co2_level ) values ( ?,?,?,?,?,?,?,?)")

    def start(self):
        self._start_sensors()

        # To be re-structured, kept for testing
        db_session = self.db_connect()
        stmt = self.get_insert_stmt(db_session)

        ## Only writes into DB
        while True:
            #csv_file = self._make_todays_csv_file_if_necessary()
            #with open(csv_file, "a") as f:

            for s in self._sensors:
                if(len(s.latest_db_data) != 0):
                    #f.write(s.ip + "," + s.name + "," + s.latest_csv_data)
                    db_session.execute(stmt, s.latest_db_data)

            #self._check_sensor_status()
            time.sleep(self._sample_interval)


if __name__ == "__main__":
    sdr = SensorDataReader("config.ini")
    sdr.start()

