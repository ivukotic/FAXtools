#!/bin/zsh
# uncomment to debug 
# uset -x

export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup

echo "deleting old files..."

WD=/afs/cern.ch/user/i/ivukotic/FAXtools/FAXconfiguration/

cd $WD
rm check*.sh *.log

source /afs/cern.ch/project/gd/LCG-share/current/etc/profile.d/grid_env.sh; 

source $AtlasSetup/scripts/asetup.sh 17.7.0,noTest

voms-proxy-init -cert /afs/cern.ch/user/i/ivukotic/.globus/usercert.pem -key /afs/cern.ch/user/i/ivukotic/.globus/userkey.pem -voms atlas -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt

source /afs/cern.ch/project/xrootd/software/setup.sh test/3.3.3-rc1/x86_64-slc6-gcc45-opt

cd $WD

python FAX_configuration_tests.py

cp *.log /afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/.

echo "Done." 
