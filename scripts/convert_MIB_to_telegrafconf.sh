#!/bin/bash

# Script to convert a given MIB file into a telegraf config file
# 
# Two output options exist:
#  A) output with each OID treated as field
#  B) output using tables + fields w/o duplicated fields
#
# TODO: get rid of deprecated OIDs 


INFILE="WR-SWITCH-MIB"
OUT_A="/tmp/snmp-all-fields.conf"
OUT_B="/tmp/snmp-with-tables.conf"


### Start of Option A ###
# get all White Rabbit related OIDs as single fields into config file
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep "1.3.6.1.4.1.96.100" | awk -F $'\t+' '{print "  [[inputs.snmp.field]]\n    name = "$1 "\n    oid = "$2}' > ${OUT_A}
### End of Option A ###



### Start of Option B ###
# 1) get only the tables and write to output file
#    - tag index of table for easier access to ports in dashboards
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep "Table" | awk -F $'"' '{print "  [[inputs.snmp.table]]\n    oid = \"WR-SWITCH-MIB::"$2"\" \n    index_as_tag = true"}' > $OUT_B

# 2) get the table OID to later remove them from fields
fOID="/tmp/tableOIDs.txt"
/usr/bin/snmptranslate -Tz -m WR-SWITCH-MIB | grep "Table" | awk -F $'"' '{print $4}' > $fOID

COMMAND=""
while read OID
do
    COMMAND+=" -e $OID" 
done < $fOID
rm -f $fOID

# 3) get all fields from MIB file which do not belong to a table
echo "" >> $OUT_B
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep 1.3.6.1.4.1.96.100 | grep -v $COMMAND | awk -F $'\t+' '{print "  [[inputs.snmp.field]]\n    name = "$1 "\n    oid = "$2}' >> $OUT_B

#TODO: change command in case no tables found! 
### End of Option B ###
