## Making use of variables within grafana dashboards 
To reduce the need of duplicating dashboards for every single WR switch or port, variables can be used. 

### Hostname 
In order to choose between different WR switches, the IP address (hostname) is used as identifier. The settings are the following:

~~~
General
Name: hostname 
Type: Query

Query options
Date source: InfluxDB telegraf 
Query: SHOW TAG VALUES WITH KEY = "agent_host"
~~~

