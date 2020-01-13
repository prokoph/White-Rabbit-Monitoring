#!/usr/bin/env python3

from pysnmp.hlapi import *
import sys

from influxdb import InfluxDBClient, DataFrameClient
host = "localhost"
port = 8086
user = "root"
password = "root"
dbname = "oszi"

client = DataFrameClient(host, port, user, password, dbname)
print("Reading database: " + dbname)

datadict = client.query("SELECT * from timing")
data = datadict["timing"]

data.to_csv("timing_Jan13.csv")
