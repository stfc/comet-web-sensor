import urllib.request
import urllib.error
import xml.etree.ElementTree as ET


class Sensor():
    
    def __init__(self,parms):
        self._ip = parms['ip']
        self._name = parms['name']
        self._parameters = ['Temperature', 'Relative humidity', 'Dew point', 'CO2 level']
        self._data_received = False
    

    def _read_xml_from_web(self):
        try:
            r = urllib.request.urlopen("http://" + self._ip + "/values.xml", timeout=2)
            self._data_received = True
            return ET.fromstring(r.read(2048))
        except (TimeoutError, urllib.error.URLError):
            self._data_received = False
            return None


    def _read_xml_from_file(self, filename = 'test_data.xml'):
        with open(filename, 'r') as f:
            data = f.read()
        self._data_received = True
        return ET.fromstring(data)

    
    def _xml_is_valid(self, xml_data):
        return xml_data[0].text != "1"


    def _make_csv_list_from_xml(self, xml_data, val_names):
        if not self._data_received:
            data_list = ['connection?'] * len(val_names)
        elif not self._xml_is_valid(xml_data):
            data_list = ['invalid'] * len(val_names)
        else:
            data = {child.findtext('name'):child.findtext('aval') for child in xml_data if child.findall("unit") }
            data_list = [data[v] for v in val_names]
        return ','.join(data_list) 

    
    def _get_latest_data(self):
        return self._make_csv_list_from_xml(self.xml_data, self._parameters)


    @property
    def xml_data(self):
        return self._read_xml_from_web()
      
    
    @property
    def latest_data(self):
        return self._get_latest_data() + '\n'

    
    @property
    def requested_data(self):
        return ','.join(self._parameters) + '\n'
    

    @requested_data.setter
    def requested_data(self, req):
        self._parameters = req


    @property
    def ip(self):
        return self._ip.replace('.','_')

    @ip.setter
    def ip(self, ip):
        self._ip = ip.replace('_','.')


    @property
    def name(self):
        return self._name



        


