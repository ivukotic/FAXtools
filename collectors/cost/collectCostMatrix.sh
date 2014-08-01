#!/bin/sh
export PATH="/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc43-opt/bin:$PATH"
export LD_LIBRARY_PATH="/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc43-opt/lib:$LD_LIBRARY_PATH"

source /afs/cern.ch/user/a/agis/public/AGISClient/latest/setup.py26.sh

cd /data/adcmusr3/

rm cost*.log

da=cost_$(date +"%Y-%m-%dT%H%M").log
./collectCostMatrix.py $da

scp cost*.log ivukotic@uct2-int.mwt2.org:/home/ivukotic/public_html/LOGS
