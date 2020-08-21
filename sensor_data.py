#!/usr/bin/env python3
from sensor_data_reader import SensorDataReader
from stats_writer import StatsWriter
import threading


if __name__ == "__main__":
    sdr = SensorDataReader("config.ini")
    sw = StatsWriter("config.ini", 60 * 60 * 2)
    reader_thread = threading.Thread(target=sdr.start, name="reader_thread")
    stats_thread = threading.Thread(target=sw.start, name="stats_thread")

    reader_thread.start()
    stats_thread.start()
