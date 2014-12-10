#!/bin/bash
for i in `seq 1 10`;
    do
        ET=$(date +%s)
        DT=60
        ST=`expr $ET - $DT`
        echo $i $ST $ET
        sed "s/STARTTIME/$ST/g" msg.xml > .msg1.xml
        sed "s/ENDTIME/$ET/g" .msg1.xml > .msg2.xml
        nc -vu 134.79.200.87 9931 < .msg2.xml
        # nc -vu atl-prod05.slac.stanford.edu 9931 < .msg2.xml
        sleep $DT
    done  
        

