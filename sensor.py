import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import datetime
import socket


class Sensor():
    
    def __init__(self,parms):
        self._ip = parms['ip']
        self._name = parms['name']
        self._data_fields = ['Time', 'Temperature', 'CO2 level']
        self._data_received = False
    
    
    def _generate_timestamp(self, format = "%m/%d/%Y %H:%M:%S"):
        return datetime.datetime.now().strftime(format)


    def _read_xml_from_web(self):
        try:
            r = urllib.request.urlopen("http://" + self._ip + "/values.xml", timeout=5)
            xml = ET.fromstring(r.read(2048))
            self._data_received = True
            return xml
        except (TimeoutError, urllib.error.URLError, socket.timeout):
            self._data_received = False
            return None


    def _read_xml_from_file(self, filename = 'test_data.xml'):
        with open(filename, 'r') as f:
            data = f.read()
        self._data_received = True
        return ET.fromstring(data)

    
    def _xml_is_valid(self, xml_data):
        return xml_data[0].text != "1"


    def _get_latest_data(self):
        xml = self._read_xml_from_web()
        if not self._data_received:
            data = self._sub_data_with_error('connection')
        elif not self._xml_is_valid(xml):
            data = self._sub_data_with_error('invalid')
        else:
            data = {child.findtext('name'):child.findtext('aval') for child in xml if child.findall("unit") }
            data = self._add_timestamp_if_required(data)
        return data 


    def _sub_data_with_error(self, reason):
        err_dict = {field:reason for field in self._data_fields}
        err_dict = self._add_timestamp_if_required(err_dict)
        return err_dict
    

    def _add_timestamp_if_required(self, data_dictionary):
            if 'Time' in self._data_fields:
                data_dictionary['Time'] = self._generate_timestamp()
            return data_dictionary


    @property
    def xml_data(self):
        return self._read_xml_from_web()
      
    
    @property
    def latest_csv_data(self):
        data_list = [self._get_latest_data()[df] for df in self._data_fields]
        return ','.join(data_list) + '\n'


    @property
    def latest_data(self):
        return self._get_latest_data()
    

    @property
    def data_fields(self):
        return ','.join(self._data_fields) + '\n'
    

    @data_fields.setter
    def data_fields(self, fields):
        self._data_fields = fields


    @property
    def ip(self):
        return self._ip.replace('.','_')


    @ip.setter
    def ip(self, ip):
        self._ip = ip.replace('_','.')


    @property
    def name(self):
        return self._name



        


