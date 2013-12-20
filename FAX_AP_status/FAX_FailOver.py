#!/usr/bin/env python
import subprocess, threading
import os, sys, time

try: 
	import simplejson as json
except ImportError: 
	import json

import urllib2

queues={}

class queue:    
    name=''
    allowdirectaccess=''
    allowfax=''
    copysetup=''
    faxredirector=''
     
    def __init__(self, na, ada, af, cs,fr):
        self.name=na
        self.allowdirectaccess=ada
        self.allowfax=af
        self.copysetup=cs
        self.faxredirector=fr
    
    def prnt(self):
        print '------------------------------------\nname:',self.name
        print 'allowdirectaccess:', self.allowdirectaccess, '\tallowfax:', self.allowfax, '\tcopysetup:', self.copysetup, '\t faxredirector:', self.faxredirector
        


try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/?json&preset=schedconf.all", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for k,v in res.items():
        #print k, v['allowdirectaccess'],v['rc_site'],v['allowfax'],v['copysetup'],v['faxredirector']
        if not v['rc_site'] in queues: queues[v['rc_site']]=[]
        queues[v['rc_site']].append( queue(k,v['allowdirectaccess'],v['allowfax'],v['copysetup'],v['faxredirector']) )
except:
    print "Unexpected error:", sys.exc_info()[0]    
    
for k,v in queues.items():
    print k
    for q in v:
        if q.allowfax: q.prnt()
        
        

print '--------------------------------- Writing Queues for twiki ----------------------------'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiEnabledQueues.log', 'w') as f: 
    f.write('| *queue* | *allowdirectaccess* | *copysetup* | *faxredirector* |\n')
    for k,v in queues.items():
        found=0
        for q in v:
            if q.allowfax: found=1
        if found: 
            f.write('| *'+k+'* |||||\n')
            for q in v:
                f.write('| '+q.name+' | '+str(q.allowdirectaccess)+ ' | '+q.copysetup+ ' | '+q.faxredirector+ '|\n')
f.close()

with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiNotEnabledQueues.log', 'w') as f: 
    f.write('| *site* | *queue* | *allowdirectaccess* | *copysetup* | *faxredirector* |\n')
    for k,v in queues.items():
        found=0
        for q in v:
            if q.allowfax: found=1
        if not found:
            f.write('| *'+k+'* |||||\n')
            for q in v:
                f.write('| '+q.name+' | '+str(q.allowdirectaccess)+ ' | '+q.copysetup+ ' | '+q.faxredirector+ '|\n')
f.close()

