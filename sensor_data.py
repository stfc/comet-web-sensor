#!/usr/bin/env python3
from sensor_data_reader import SensorDataReader
from stats_writer import StatsWriter
import threading, logging
from configparser import ConfigParser

config_file = "config.ini"
cp = ConfigParser()
cp.read(config_file)
debug = cp.getboolean("logging", "debug")

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting up")
    sdr = SensorDataReader("config.ini")
    logger.info("Loaded sensor config")
    sw = StatsWriter("config.ini", 60 * 60 * 2)
    logger.info("Initialised data store")
    reader_thread = threading.Thread(target=sdr.start, name="reader_thread")
    stats_thread = threading.Thread(target=sw.start, name="stats_thread")

    reader_thread.start()
    stats_thread.start()
