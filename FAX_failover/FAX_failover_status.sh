#!/bin/zsh
# uncomment to debug 
# uset -x

WD=/data/adcmusr3/FAXtools/FAX_failover

cd $WD
./FAX_failover_status.py

echo "Done." 
