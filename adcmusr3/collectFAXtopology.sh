#!/bin/sh

export PATH="/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc43-opt/bin:$PATH"
export LD_LIBRARY_PATH="/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc43-opt/lib:$LD_LIBRARY_PATH"

source /afs/cern.ch/user/a/agis/public/AGISClient/latest/setup.py26.sh

cd ~/FAXtools/adcmusr3/
python collectFAXtopology.py

python collectFAXredirectors.py

python generateInstantMails.py

