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
     
    def __init__(self, na, sink, source ):
        self.name=na
        self.sink=sink
        self.source=source
    
    def prnt(self):
        print 'name:',self.name, '\twansinklimit:', self.sink, '\twansourcelimit:', self.source
        


try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/?json&preset=schedconf.all&vo_name=atlas", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for k,v in res.items():
        #print k, v['allowdirectaccess'],v['rc_site'],v['allowfax'],v['copysetup'],v['faxredirector']
        if v['wansinklimit']>0 or v['wansourcelimit']>0 :
            if not v['rc_site'] in queues: queues[v['rc_site']]=[]
            queues[v['rc_site']].append( queue(k,v['wansinklimit'],v['wansourcelimit']) )
except:
    print "Unexpected error:", sys.exc_info()[0]    
    
for k,v in queues.items():
    print k
    for q in v:
        q.prnt()
        
        

print '--------------------------------- Writing Queues for twiki ----------------------------'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiOverflowQueues.log', 'w') as f: 
    f.write('| *queue* | *WANsinklimit* | *WANsourcelimit* |\n')
    for k,v in queues.items():
        f.write('| *'+k+'* ||||\n')
        for q in v:
            f.write('| '+q.name+' | '+str(q.sink)+ ' | '+str(q.source)+ ' |\n')
f.close()

