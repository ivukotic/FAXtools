#!/bin/zsh
# uncomment to debug 
# uset -x

export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup

echo "deleting old files..."

WD=/afs/cern.ch/user/i/ivukotic/FAXtools/FAXconfiguration/

cd $WD
rm check*.sh *.log

source /afs/cern.ch/project/gd/LCG-share/current/etc/profile.d/grid_env.sh; 

source $AtlasSetup/scripts/asetup.sh 17.6.0,noTest

voms-proxy-init -cert /afs/cern.ch/user/i/ivukotic/.globus/usercert.pem -key /afs/cern.ch/user/i/ivukotic/.globus/userkey.pem -voms atlas -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt

cd $WD

python FAX_delays_tests.py

cp *.log /afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/.

echo "Done." 
