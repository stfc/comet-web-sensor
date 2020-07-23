#!/usr/bin/env python3
import os, datetime, time, atexit
from pathlib import Path
from sensor import Sensor



def get_today():
    return datetime.date.today().strftime("%Y%m%d")
    

def make_dir_if_needed(filename):
    directory, _ = os.path.split(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)


def generate_sensor_filename(sensor, root = os.getcwd()):
    return root + os.sep + get_today() + os.sep + get_today() + '_' + sensor.ip + '.csv'


def generate_todays_filename(root = os.getcwd()):
    return root + os.sep + get_today() + '_sensors' + '.csv'


def make_sensor_csv_file_if_necessary(sensor, root = os.getcwd()):
    filename = generate_sensor_filename(sensor, root)
    if not Path(filename).is_file(): 
        make_dir_if_needed(filename)
        with open(filename, 'w') as f:
            f.write(sensor.data_fields)
    return filename

def make_todays_csv_file_if_necessary(fields, root = os.getcwd()):
    filename = generate_todays_filename(root)
    if not Path(filename).is_file(): 
        make_dir_if_needed(filename)
        with open(filename, 'w') as f:
            f.write(fields)
    return filename


if __name__ == "__main__":

    sensor_parms = [{'ip':'130.246.68.74', 'name':'R1 Mech Zund'},
                    {'ip':'130.246.68.75', 'name':'R1 T-fab office'},
                    {'ip':'130.246.68.81', 'name':'R1 Gemini office'},
                    {'ip':'130.246.68.82', 'name':'R1 Mech CNC'},
                    {'ip':'130.246.68.87', 'name':'RCaH1'},
                    {'ip':'130.246.68.88', 'name':'R1 Mech Assy'},
                    {'ip':'130.246.68.90', 'name':'R1 Directorate'},
                    {'ip':'130.246.68.91', 'name':'RCaH2'},
                    {'ip':'130.246.68.92', 'name':'R1 Mech office'},
                    {'ip':'130.246.68.94', 'name':'Mobile unit'},
                    {'ip':'130.246.68.111', 'name':'R1 VCR'},
                    {'ip':'130.246.68.112', 'name':'R1 Mech Manual'},
                    {'ip':'130.246.68.114', 'name':'R1 CALTA offices'},
                    {'ip':'130.246.68.121', 'name':'R1 Theory offices'},
                    {'ip':'130.246.68.111', 'name':'R1 Electrical offices'}]


    sensors = [Sensor(parms) for parms in sensor_parms]

    fields = ['Temperature', 'Relative humidity', 'Dew point', 'CO2 level']

    interval = 60

    for sensor in sensors:
        sensor.data_fields = fields
        sensor.start_data_collection(interval=interval)
    
          
    def generate_timestamp(format = "%m/%d/%Y %H:%M:%S"):
        return datetime.datetime.now().strftime(format)
    
    

    if __name__ == '__main__':
        while True:
            # Stuff for Steve Blake - one file per sensor per day
            for sensor in sensors:
                csv_file = make_sensor_csv_file_if_necessary(sensor, root='/opt/sensor_data/sensor_data')
                with open(csv_file, 'a') as f:
                    f.write(sensor.latest_csv_data)
                
            # Stuff for Dash
                csv_file_dash = make_todays_csv_file_if_necessary('ip,name,' + ','.join(fields)+'\n', root='/opt/sensor_data/dash')
                with open(csv_file_dash, 'a') as f:
                    f.write(sensor.ip+','+sensor.name+','+sensor.latest_csv_data)
            time.sleep(interval)
            
            



