#!/bin/bash
for i in `seq 1 10`;
    do
        timestamp=$(date +%s)
        echo $i $timestamp
        sed -i 's/ENDTIME/$timestamp/g' msg.xml msgts.xml
        cat msgts.xml | nc -u atl-prod05.slac.stanford.edu 9931
    done  
        

