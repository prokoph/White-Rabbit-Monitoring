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

    IP = [ '192.168.4.35', '192.168.4.165' ]
    OID = dict(
        cpu15min='1.3.6.1.4.1.96.100.7.1.5.3',
        #wrsPtpServoState='1.3.6.1.4.1.96.100.7.5.1.6',
        #wrsPtpRTT='1.3.6.1.4.1.96.100.7.5.1.13.1',
        #wrsPtpDeltaTxM='1.3.6.1.4.1.96.100.7.5.1.16',
        #wrsPtpDeltaRxM='1.3.6.1.4.1.96.100.7.5.1.17',
        #wrsPtpDeltaTxS='1.3.6.1.4.1.96.100.7.5.1.18',
        #wrsPtpDeltaRxS='1.3.6.1.4.1.96.100.7.5.1.19',
        #wrsDateTAI='1.3.6.1.4.1.96.100.7.1.1.1',
        #wrsMainSystemStatus='1.3.6.1.4.1.96.100.6.1.1',
        #wrsOSStatus='1.3.6.1.4.1.96.100.6.1.2',
        #wrsTimingStatus='1.3.6.1.4.1.96.100.6.1.3',
        #wrsNetworkingStatus='1.3.6.1.4.1.96.100.6.1.4',
        #wrsSpllMode='1.3.6.1.4.1.96.100.7.3.2.1',
        #wrsSoftPLLStatus='1.3.6.1.4.1.96.100.6.2.2.2'
    )

    interval = 10

    try:
        while True:
            for switch in IP:
                out = {}
                for key,value in OID.items():
                    out[key] = walk( switch, value )

                json_body = [
                    {
                        "measurement": "CPU",
                        "tags": {
                            "hostname": switch,
                        },
                        "fields": out
                    }
                ]

                # Write JSON to InfluxDB
                client.write_points(json_body)
                #print(json_body)

            # Wait for next sample
            sleep(interval)
                                                    
            
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    main()
