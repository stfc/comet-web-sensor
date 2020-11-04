import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime as dt
import logging
import time
import socket
import threading
import http.client
from pytz import timezone
from cassandra.cluster import Cluster


class Sensor:
    def __init__(self, parms):
        self._ip = parms["ip"]
        self._name = parms.get("name", self._ip)
        self._contact_email = parms.get("email", "an.address@stfc.ac.uk")
        self._data_fields = [
            "Time",
            "Temperature",
            "Relative humidity",
            "Dew point",
            "CO2 level",
        ]
        self._latest_data = {
            "Time": self._generate_timestamp(),
            "Temperature": "-",
            "Relative humidity": "-",
            "Dew point": "-",
            "CO2 level": "-",
        }
        self._data_received = False
        self._last_successful_read = dt.now()
        self._read_thread = None

    def _format_timestamp(self, isotime, format="%m/%d/%Y %H:%M:%S"):
        return (
            dt.fromisoformat(isotime)
            .astimezone(timezone("Europe/London"))
            .strftime(format)
        )

    def _generate_timestamp(self, format="%m/%d/%Y %H:%M:%S"):
        return dt.now().strftime(format)

    def _read_xml_from_web(self):
        try:
            r = urllib.request.urlopen("http://" + self._ip + "/values.xml", timeout=10)
            xml = ET.fromstring(r.read(2048))
            self._data_received = True
            return xml
        except (
            TimeoutError,
            urllib.error.URLError,
            socket.timeout,
            http.client.BadStatusLine,
        ) as e:
            logging.warning("sensor ({}) read error: {}".format(self._name, str(e)))
        except Exception as e:
            logging.error(
                "sensor ({}) unexpected error on read: {}".format(self._name, str(e))
            )
        self._data_received = False
        return None

    def _read_xml_from_file(self, filename="test_data.xml"):
        with open(filename, "r") as f:
            data = f.read()
        self._data_received = True
        return ET.fromstring(data)

    def _xml_is_valid(self, xml_data):
        return xml_data[0].text != "1"

    def _get_latest_data(self, interval=60):
        while True:
            xml = self._read_xml_from_web()
            # xml = self._read_xml_from_file()
            if not self._data_received:
                data = self._sub_data_with_error(0)
            elif not self._xml_is_valid(xml):
                data = self._sub_data_with_error(0)
            else:
                data = {
                    child.findtext("name"): child.findtext("aval")
                    for child in xml
                    if child.findall("unit")
                }
                time_string = xml.findtext("time")
                data["Time"] = self._format_timestamp(time_string)
                self._last_successful_read = dt.strptime(
                    data["Time"], "%m/%d/%Y %H:%M:%S"
                )
            self._latest_data = data
            logging.info("sensor ({}) sent: {}".format(self._name, data))
            time.sleep(interval)

    def _sub_data_with_error(self, reason):
        err_dict = {field: reason for field in self._data_fields}
        err_dict["Time"] = self._generate_timestamp()
        return err_dict

    @property
    def seconds_since_successful_read(self):
        return (dt.now() - self._last_successful_read).seconds

    @property
    def time_of_last_successful_read(self):
        return self._last_successful_read.strftime(format="%m/%d/%Y %H:%M:%S")

    @property
    def xml_data(self):
        return self._read_xml_from_web()

    @property
    def latest_csv_data(self):
        data_list = [self._latest_data[df] for df in self._data_fields]
        return ",".join(data_list) + "\n"
    
    @property
    def latest_db_data(self):
        if any(v in self._latest_data.values() for v in ['-', 'connection', 0]):
            return []
            
        data_list = []
        data_list.append(self._ip)
        data_list.append(self._name)
        data_list.append(dt.strptime(self._latest_data["Time"], "%m/%d/%Y %H:%M:%S"))
        data_list.append(dt.strptime(self._latest_data["Time"], "%m/%d/%Y %H:%M:%S"))
        data_list.append(float(self._latest_data["Temperature"]))
        data_list.append(float(self._latest_data["Relative humidity"]))
        data_list.append(float(self._latest_data["Dew point"]))
        data_list.append(float(self._latest_data["CO2 level"]))

        return data_list

    @property
    def latest_data(self):
        return self._latest_data

    @property
    def data_fields(self):
        return ",".join(self._data_fields) + "\n"

    @data_fields.setter
    def data_fields(self, fields):
        pass

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        self._ip = ip.replace("_", ".")

    @property
    def name(self):
        return self._name

    @property
    def contact_email(self):
        return self._contact_email

    def start_data_collection(self, interval=60):
        if not self._read_thread:
            self._read_thread = threading.Thread(
                target=self._get_latest_data, name="data_thread", args=(interval,)
            )
            self._read_thread.start()
        else:
            print("Data collection thread already running")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = Sensor({"ip": "1.2.3.4", "name": "test_sensor"})
    s.start_data_collection(10)
