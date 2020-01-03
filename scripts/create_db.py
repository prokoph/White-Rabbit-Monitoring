#!/usr/bin/env python3

from pysnmp.hlapi import *
from time import sleep
import sys

from influxdb import InfluxDBClient
host = "localhost"
port = 8086
user = "root"
password = "root"
dbname = "oszi"

client = InfluxDBClient(host, port, user, password, dbname)
print("Create database: " + dbname)
client.create_database(dbname)

