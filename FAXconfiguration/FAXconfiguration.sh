#!/bin/bash
# uncomment to debug 
# uset -x

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
export RUCIO_ACCOUNT=ivukotic
#localSetupFAX --xrootdVersion=3.3.6-x86_64-slc6
localSetupFAX --xrootdVersion=4.0.2-x86_64-slc6

voms-proxy-init -cert /afs/cern.ch/user/i/ivukotic/.globus/usercert.pem -key /afs/cern.ch/user/i/ivukotic/.globus/userkey.pem -voms atlas -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt

echo "deleting old files..."

WD=/afs/cern.ch/user/i/ivukotic/FAXtools/FAXconfiguration/
cd $WD
rm check*.sh 
rm *.log 
rm *.zip

python FAX_configuration_tests.py

#copy to afs web space
#cp *.log /afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/.

#upload to FAXBOX
#da=$(date +"%Y-%m-%dT%H%M")
#zip SSB_FAX_endpoints_logs-$da.zip *.log
#xrdcp SSB_FAX_endpoints_logs-$da.zip root://faxbox.usatlas.org//user/ivukotic

ls *.log

echo "upload all the logs to GAE blobservice"
date

rv=" -F file=@"
upload_url=`curl http://waniotest.appspot.com/LogUpload.jsp`

echo -n "curl -vX POST  " > tr1.sh 
for f in *_to_*.log; do echo -n "${rv}${f} " >> tr1.sh; done
echo $upload_url >> tr1.sh

echo -n "curl -vX POST  " >> tr1.sh 
for f in downstreamTo_*.log; do echo -n "${rv}${f} " >> tr1.sh; done
echo $upload_url >> tr1.sh

echo -n "curl -vX POST  " >> tr1.sh 
for f in upstreamFrom_*.log; do echo -n "${rv}${f} " >> tr1.sh; done
echo $upload_url >> tr1.sh

echo -n "curl -vX POST  " >> tr1.sh 
for f in checkSecurity*.log; do echo -n "${rv}${f} " >> tr1.sh; done
echo $upload_url >> tr1.sh

#echo -n "curl -vX POST  " >> tr1.sh 
#for f in checkDelays*.log; do echo -n "${rv}${f} " >> tr1.sh; done
#echo $upload_url >> tr1.sh

echo -n "curl -vX POST  " >> tr1.sh 
for f in checkRedirector*.log; do echo -n "${rv}${f} " >> tr1.sh; done
echo $upload_url >> tr1.sh

chmod +x tr1.sh
./tr1.sh

#fl="";for f in *_to_*.log; do fl="$fl -F file=$f"; done
#upload_url=`curl http://waniotest.appspot.com/LogUpload.jsp`; curl -vX POST $fl $upload_url


date

#copy to MWT2 web space
#scp *.log uct2-int.mwt2.org:/home/ivukotic/public_html/LOGS

killall -9 xrdcp

killall -9 xrdfs

killall -9 scp
echo "Done." 
