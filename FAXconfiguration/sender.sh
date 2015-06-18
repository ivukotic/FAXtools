cd /home/ivukotic/FAXtools/FAXconfiguration/t
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
source ${ATLAS_LOCAL_ROOT_BASE}/packageSetups/atlasLocalFAXSetup.sh --faxtoolsVersion ${faxtoolsVersionVal}
voms-proxy-init -valid 24:0 -voms atlas -pwstdin < /home/ivukotic/gridlozinka.txt
../FAX_summary_collector.py > sender.log 2>&1
