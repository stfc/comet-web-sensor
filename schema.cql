CREATE KEYSPACE IF NOT EXISTS sensors WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1} ;
USE sensors;
CREATE TABLE IF NOT EXISTS sensors (
	ip INET
, name TEXT
,	last_read TIMESTAMP
,	online BOOLEAN
,	PRIMARY KEY(ip)
);
CREATE TABLE IF NOT EXISTS sensors_data (
	ip INET
, name TEXT
, date DATE
, datetime TIMESTAMP
, temperature FLOAT
, relative_humidity FLOAT
, dew_point FLOAT
, co2_level FLOAT
, PRIMARY KEY((ip, date), datetime)
);
CREATE INDEX info_date ON sensors_data (date);
CREATE TABLE IF NOT EXISTS co2_level (
	date DATE
, ip INET
, name TEXT
, peak FLOAT
, mean FLOAT
, std FLOAT
, PRIMARY KEY(date, ip)
);
CREATE TABLE IF NOT EXISTS dew_point (
	date DATE
, ip INET
, name TEXT
, peak FLOAT
, mean FLOAT
, std FLOAT
, PRIMARY KEY(date, ip)
);
CREATE TABLE IF NOT EXISTS relative_humidity (
	date DATE
, ip INET
, name TEXT
, peak FLOAT
, mean FLOAT
, std FLOAT
, PRIMARY KEY(date, ip)
);
CREATE TABLE IF NOT EXISTS temperature (
	date DATE
, ip INET
, name TEXT
, peak FLOAT
, mean FLOAT
, std FLOAT
, PRIMARY KEY(date, ip)
);
