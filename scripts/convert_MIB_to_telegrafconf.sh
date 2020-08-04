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
# get all White Rabbit related OIDs as single fields into config file (adds .0 to oid)
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep "1.3.6.1.4.1.96.100" | grep -v Group | awk -F $'\t+' '{print $1 " " $2}' | sed 's/"//g' | awk '{print "  [[inputs.snmp.field]]\n    name = \""$1"\"\n    oid = \""$2".0\""}' > ${OUT_A}
### End of Option A ###


### Start of Option B ###
# 1) get only the tables and write to output file
#    - tag index of table for easier access to ports in dashboards
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep "Table" | awk -F $'"' '{print "  [[inputs.snmp.table]]\n    oid = \"WR-SWITCH-MIB::"$2"\" \n    index_as_tag = true"}' > $OUT_B

# 2) get the table OID to later remove them from fields
fOID="/tmp/tableOIDs.txt"
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep "Table" | awk -F $'"' '{print $4}' > $fOID

# do not bother telegraf with the naming convention/scalar definition fields
COMMAND=" -e wrSwitchMIB -e 1.3.6.1.4.1.96.100.1"
while read OID
do
    COMMAND+=" -e $OID" 
done < $fOID
rm -f $fOID

# 3) get all fields from MIB file which do not belong to a table
echo "" >> $OUT_B
/usr/bin/snmptranslate -Tz -m ${INFILE} | grep 1.3.6.1.4.1.96.100 | grep -v $COMMAND | grep -v Group | awk -F $'\t+' '{print $1 " " $2}' | sed 's/"//g' | awk '{print "  [[inputs.snmp.field]]\n    name = \""$1"\"\n    oid = \""$2".0\""}' >> $OUT_B
### End of Option B ###
