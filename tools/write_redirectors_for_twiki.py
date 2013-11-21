#!/usr/bin/env python

import os, sys 
import urllib2,simplejson

#print 'Geting data from AGIS ...'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiRedirectors.log', 'w') as fi:
    fi.write("| *Site* | *Address* |\n")
    try:
        req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_redirector_services/?json&state=ACTIVE", None)
        opener = urllib2.build_opener()
        f = opener.open(req)
        res=simplejson.load(f)
        for s in res:
             l="| "+s["rc_site"]+" | "+s["endpoint"]+" |\n"
             # print l
             fi.write(l)
        print "got FAX redirectors from AGIS."

    except:
        print "Unexpected error:", sys.exc_info()[0]    

    fi.close()
