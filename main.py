import os, datetime, time
from pathlib import Path
from sensor import Sensor


def get_today():
    return datetime.date.today().strftime("%Y%m%d")
    

def make_dir_if_needed(filename):
    directory, _ = os.path.split(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)


def generate_filename(sensor):
    return os.getcwd() + os.sep + get_today() + os.sep + get_today() + '_' + sensor.name + '.csv'


def make_csv_file_if_necessary(sensor):
    filename = generate_filename(sensor)
    if not Path(filename).is_file(): 
        make_dir_if_needed(filename)
        with open(filename, 'w') as f:
            f.write(sensor.data_fields)
    return filename


if __name__ == "__main__":

    sensor_parms = [{'ip':'130.246.68.74', 'name':'Room1'},
                    {'ip':'130.246.68.75', 'name':'Room2'},
                    {'ip':'130.246.68.81', 'name':'Room3'},
                    {'ip':'130.246.68.82', 'name':'Room4'},
                    {'ip':'130.246.68.87', 'name':'Room5'},
                    {'ip':'130.246.68.88', 'name':'Room6'},
                    {'ip':'130.246.68.90', 'name':'Room7'},
                    {'ip':'130.246.68.91', 'name':'Room8'},
                    {'ip':'130.246.68.92', 'name':'Room9'},
                    {'ip':'130.246.68.94', 'name':'Room10'}]

    sensors = [Sensor(parms) for parms in sensor_parms]

    for sensor in sensors:
        sensor.data_fields = ['Time', 'Temperature', 'Relative humidity', 'Dew point', 'CO2 level']

    interval = 60   
    
    while True:
        for sensor in sensors:
            csv_file = make_csv_file_if_necessary(sensor)
            with open(csv_file, 'a') as f:
                f.write(sensor.latest_csv_data)
        time.sleep(interval)