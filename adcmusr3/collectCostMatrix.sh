#!/bin/sh

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
export RUCIO_ACCOUNT=adcmusr3
localSetupAGIS

cd ~/FAXtools/adcmusr3/

rm cost*.log

da=cost_$(date +"%Y-%m-%dT%H%M").log
./collectCostMatrix.py /data/www/FAX/ $da

scp cost*.log ivukotic@uct2-int.mwt2.org:/home/ivukotic/public_html/LOGS
