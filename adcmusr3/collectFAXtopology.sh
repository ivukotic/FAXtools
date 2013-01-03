#!/bin/zsh

export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup
source $AtlasSetup/scripts/asetup.sh 17.6.0,noTest

cd /data/adcmusr3/
python  collectFAXtopology.py
