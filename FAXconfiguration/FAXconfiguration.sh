#!/bin/zsh
# uncomment to debug 
# uset -x

export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup

echo "deleting old files..."

WD=/afs/cern.ch/user/i/ivukotic/FAXtools/FAXconfiguration/

cd $WD
rm checkRedirection.sh checkUpDown.sh toExecute.sh *.log

source /afs/cern.ch/project/gd/LCG-share/current/etc/profile.d/grid_env.sh; 

source $AtlasSetup/scripts/asetup.sh 17.6.0,noTest

voms-proxy-init -voms atlas -pwstdin < $WD/gridlozinka.txt

cd $WD

python FAX_configuration_tests.py

echo "Done." 
