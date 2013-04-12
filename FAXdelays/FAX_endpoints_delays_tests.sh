#!/bin/zsh
# uncomment to debug 
# uset -x

export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup

echo "deleting old files..."

WD=$HOME/FAXtools/FAXdelays/

cd $WD
rm check*.sh *.log

source /afs/cern.ch/project/gd/LCG-share/current/etc/profile.d/grid_env.sh; 

source $AtlasSetup/scripts/asetup.sh 17.6.0,noTest

voms-proxy-init -cert $HOME/.globus/usercert.pem -key $HOME/.globus/userkey.pem -voms atlas -pwstdin < $HOME/gridlozinka.txt

cd $WD

python FAX_endpoints_delays_tests.py

cp *.log $HOME/www/logs/FAXconfiguration/.

echo "Done." 
