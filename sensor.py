import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import datetime
import time
import socket
import threading
import http.client


class Sensor:
    def __init__(self, parms):
        self._ip = parms["ip"]
        self._name = parms["name"]
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
        self._read_thread = None

    def _generate_timestamp(self, format="%m/%d/%Y %H:%M:%S"):
        return datetime.datetime.now().strftime(format)

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
        ):
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
                data = self._sub_data_with_error("connection")
            elif not self._xml_is_valid(xml):
                data = self._sub_data_with_error("invalid")
            else:
                data = {
                    child.findtext("name"): child.findtext("aval")
                    for child in xml
                    if child.findall("unit")
                }
                data["Time"] = self._generate_timestamp()
            self._latest_data = data
            time.sleep(interval)

    def _sub_data_with_error(self, reason):
        err_dict = {field: reason for field in self._data_fields}
        err_dict["Time"] = self._generate_timestamp()
        return err_dict

    @property
    def xml_data(self):
        return self._read_xml_from_web()

    @property
    def latest_csv_data(self):
        data_list = [self._latest_data[df] for df in self._data_fields]
        return ",".join(data_list) + "\n"

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

    def start_data_collection(self, interval=60):
        if not self._read_thread:
            self._read_thread = threading.Thread(
                target=self._get_latest_data, name="data_thread", args=(interval,)
            )
            self._read_thread.start()
        else:
            print("Data collection thread already running")
            