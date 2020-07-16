import os, datetime, time, atexit
from pathlib import Path
from sensor import Sensor
from twisted.internet import task, reactor


def get_today():
    return datetime.date.today().strftime("%Y%m%d")
    

@atexit.register
def on_exit():
    reactor.stop()

def make_dir_if_needed(filename):
    directory, _ = os.path.split(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)


def generate_filename(sensor, root = os.getcwd()):
    return root + os.sep + get_today() + os.sep + get_today() + '_' + sensor.ip + '.csv'


def make_csv_file_if_necessary(sensor, root = os.getcwd()):
    filename = generate_filename(sensor, root)
    if not Path(filename).is_file(): 
        make_dir_if_needed(filename)
        with open(filename, 'w') as f:
            f.write(sensor.data_fields)
    return filename


if __name__ == "__main__":

    sensor_parms = [{'ip':'130.246.68.74', 'name':'Sensor1'},
                    {'ip':'130.246.68.75', 'name':'Sensor2'},
                    {'ip':'130.246.68.81', 'name':'Sensor3'},
                    {'ip':'130.246.68.82', 'name':'Sensor4'},
                    {'ip':'130.246.68.87', 'name':'Sensor5'},
                    {'ip':'130.246.68.88', 'name':'Sensor6'},
                    {'ip':'130.246.68.90', 'name':'Sensor7'},
                    {'ip':'130.246.68.91', 'name':'Sensor8'},
                    {'ip':'130.246.68.92', 'name':'Sensor9'},
                    {'ip':'130.246.68.94', 'name':'Sensor10'}]

    sensors = [Sensor(parms) for parms in sensor_parms]


    for sensor in sensors:
        sensor.data_fields = ['Time', 'Temperature', 'Relative humidity', 'Dew point', 'CO2 level']
    
    
    def get_data():
        for sensor in sensors:
            csv_file = make_csv_file_if_necessary(sensor, root='/home/jqg93617')
            with open(csv_file, 'a') as f:
                f.write(sensor.latest_csv_data)


    interval = 60.0 
    loop = task.LoopingCall(get_data)
    loop.start(interval)
    reactor.run()
