# comet-web-sensor
STFC-wide project to collect and graph data from Comet T6640 networkable environment monitors. Collects CO2 PPM, temperature, relative humidity and dew point from one or more sensors via HTTP.

**Currently in development - instructions below are NOT production-ready.**

## Requirements
- Apache Cassandra data store (https://cassandra.apache.org/download/)
- Python3 (3.7+ Preferred)
- python3-cassandra
- Pip

## Setup using Makefile
'Run make'
- Python requiremetns will be installed in a virtual environment in the TOP directory
- DB will be install on host

## Setup manual
1. Install Apache Cassandra
1. Import schema with `cqlsh --file schema.cql`
1. Create a Python virtual environment (optional but recommended)
1. Install Pip requirements with `pip3 install -r requirements.txt`

## Running Data Collection
From a shell, execute `./sensor_data.py`. This runs until terminated.

## Running web UI
From a shell, execute `./server-ui.py`. This starts a Flask server that runs until terminated. The server can be accessed on port 8051 by default.

## Configuration
Edit `config.ini`. Sensors can be added in the `[sensors]` section in the format `IP address: Display name`. Polling interval is configurable (60s by default).
