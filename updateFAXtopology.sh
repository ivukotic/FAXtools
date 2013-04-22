#!/bin/zsh
source /afs/cern.ch/user/i/ivukotic/.zshrc

# uncomment to debug 
# uset -x

echo "deleting old files..."

rm checkRedirection.sh checkUpDown.sh toExecute.sh *.log

source /afs/cern.ch/project/gd/LCG-share/current/etc/profile.d/grid_env.sh; 

asetup 17.7.0,noTest

voms-proxy-init -voms atlas -pwstdin < $HOME/gridlozinka.txt

cd $HOME/FAXtools/

python FAX_configuration_tests.py

echo "Done." 

#moving files to web dir

base=$HOME/www/logs/FAXtopo

d="$(date +%a)"
webdir=$base/$d
rm -rf $webdir
mkdir -p $webdir

mv *.log toExecute.sh checkRedirection.sh checkUpDown.sh $webdir/.

echo "Done."

