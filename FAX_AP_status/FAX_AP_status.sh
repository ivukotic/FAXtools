#!/bin/zsh
# uncomment to debug 
# uset -x

export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup

echo "deleting old files..."

WD=/afs/cern.ch/user/i/ivukotic/FAXtools/FAX_AP_status/

cd $WD
rm checkAP*.sh checkAP_*.log

#source /afs/cern.ch/project/gd/LCG-share/current/etc/profile.d/grid_env.sh; 
#source $AtlasSetup/scripts/asetup.sh 17.8.0,noTest
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh

localSetupGLite
localSetupPython 2.6.5-x86_64-slc5-gcc43

voms-proxy-init -cert /afs/cern.ch/user/i/ivukotic/.globus/usercert.pem -key /afs/cern.ch/user/i/ivukotic/.globus/userkey.pem -voms atlas -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt

asetup 17.8.0,noTest

source /afs/cern.ch/project/xrootd/software/setup.sh test/3.3.3-rc1/x86_64-slc6-gcc45-opt

cd $WD
python FAX_AP_status.py

cp checkAP_*.log /afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/.

killall -9 xrdfs

echo "Done." 
