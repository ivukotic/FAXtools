###################################
# author: lorenzo.rinaldi@cern.ch #
###################################


import sys, string, re, os
from agis.api.AGIS import AGIS
AGIS_API='atlas-agis-api.cern.ch:80'
#AGIS_API='atlas-agis-api-dev.cern.ch:80'

try:
    agis = AGIS(hostp=AGIS_API)
except ValueError:
    print "Error in AGIS: please, contact atlas-adc-ssb-devs@listbox.cern.ch"
    sys.exit(-1)


if len(agis.list_sites_names()) == 0:
    print "AGIS records empty: please, contact atlas-adc-ssb-devs@listbox.cern.ch"
    sys.exit(-2)

