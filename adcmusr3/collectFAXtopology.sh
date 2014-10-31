#!/bin/sh

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
export RUCIO_ACCOUNT=adcmusr3
localSetupAGIS


cd ~/FAXtools/adcmusr3/ 
python collectFAXtopology.py /data/www/FAX

python collectFAXredirectors.py /data/www/FAX

python generateInstantMails.py /data/www/FAX
