#!/bin/zsh
# uncomment to debug 
# uset -x
export RUCIO_ACCOUNT=ivukotic
export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup

echo "deleting old files..."

WD=/afs/cern.ch/user/i/ivukotic/FAXtools/FAX_AP_status/

cd $WD

python sumUP.py

rm checkAP*.sh checkAP_*.log

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh

localSetupFAX

voms-proxy-init -cert /afs/cern.ch/user/i/ivukotic/.globus/usercert.pem -key /afs/cern.ch/user/i/ivukotic/.globus/userkey.pem -voms atlas -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt


cd $WD
python FAX_AP_status.py

cp checkAP_*.log /afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/.

killall -9 xrdfs


python FAX_FailOver.py

echo "Done." 
