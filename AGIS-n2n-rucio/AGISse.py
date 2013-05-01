#!/usr/bin/env python

import os, sys
import urllib2,simplejson

out=[]

try:
    # req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&flavour=XROOTD", None)
    req = urllib2.Request("http://atlas-agis-api-dev.cern.ch/request/service/query/get_se_services/?json&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=simplejson.load(f)
    for s in res:
        si={}
        si['rc_site']=s["rc_site"]
        si['aprotocols']=[]
        #print  s["rc_site"], s["flavour"], s["endpoint"]
        #print 'aprotocols:'
        pro=s["aprotocols"]
        if 'r' in pro:
            pr=pro['r']
            for p in pr:
                si['aprotocols'].append(p[2])
        #        print '\t', p
        #print '-------------------------------'
        if len(si['aprotocols'])>0:
            out.append(si)
    print (simplejson.dumps(out, sort_keys=True, indent=4))
except:
    print "Unexpected error:", sys.exc_info()[0]    
