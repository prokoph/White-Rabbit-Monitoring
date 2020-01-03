#!/usr/bin/env python3

from pysnmp.hlapi import *
from time import sleep
import sys

from influxdb import InfluxDBClient
host = "localhost"
port = 8086
user = "root"
password = "root"
dbname = "WRSmon"

#client = InfluxDBClient(host, port, user, password, dbname)
#print("Create database: " + dbname)
#client.create_database(dbname)

def walk(host, oid):
    
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('public'),
                              UdpTransportTarget((host, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid)),
                              lookupMib=False,
                              lexicographicMode=False):

        if errorIndication:
            print(errorIndication, file=sys.stderr)
            break

        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), file=sys.stderr)
            break

        else:
            for varBind in varBinds:
                #print('%s = %s' % varBind)
                return int(varBind[1])



def main():
    '''
    Read only one OID from a WRS to long-term monitor the CPU behavior
    snmpwalk -v 2c -c public 192.168.4.165 1.3.6.1.4.1.96.100.7.1.5.3.0
    '''
    client = InfluxDBClient(host, port, user, password, dbname)
    
    wrs5 = '192.168.4.35'
    wrs6 = '192.168.4.165'
    OID = '1.3.6.1.4.1.96.100.7.1.5.3'

    interval = 10

    try:
        while True:
            cpuload_wrs5 = walk( wrs5, OID )
            json_body = [
                {
                    "measurement": "CPU",
                    "tags": {
                        "hostname": wrs5,
                    },
                    "fields": {
                        "cpu15min" : cpuload_wrs5
                    }
                }
            ]
            # Write JSON to InfluxDB
            client.write_points(json_body)
            
            cpuload_wrs6 = walk( wrs6, OID )
            json_body = [
            {
                "measurement": "CPU",
                "tags": {
                    "hostname": wrs6,
                },
                "fields": {
                    "cpu15min" : cpuload_wrs6
                }
            }
            ]
            # Write JSON to InfluxDB
            client.write_points(json_body)

            # Wait for next sample
            sleep(interval)
                                                    
            
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    main()
