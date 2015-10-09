export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
lsetup fax
voms-proxy-init -valid 24:0 -voms atlas:/atlas/Role=production -pwstdin < $HOME/gridlozinka.txt

dq2-ls -r user.ivukotic.xrootd.* > datasets.txt
cd $HOME/FAXtools/tools
./CheckTestFiles.py

