# WRS monitoring

This repository contains different scripts and tools in order to monitor the performance and characterize the behavior of a White Rabbit System. 

## General Structure

The monitoring of the WR switches is primarily done using SNMP. The current setup is that all the data is acquired using the TICKS stack (influxDB, telegraf, grafana). Additional monitoring scripts exist to ease the acquisition of additional monitoring data and check the influene on snmp requests on the preformance. 

### Prerequitites 

1. net-snmp installation with the WR-SWITCH-MIB file located in the main snmp lib directory
2. influxDB for storing the data in a nice format
3. telegraf to collect all the different metrices
4. grafana for displaying all the metrices on a nice dashboard

### Subdirectories

1. scripts for all kind of tiny snippets to get data, store them in databases
2. dashboards for different purposes of monitoring

