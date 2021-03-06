#!/usr/bin/env python
import subprocess, threading
import os, sys, time, datetime

try: 
	import simplejson as json
except ImportError: 
	import json

import urllib2

import xml.etree.ElementTree as ET


sites=[]; # each site contains [name, host, redirector]
redirectors=[]

class site:    
    name=''
    fullname=''
    host=''
    redirector=''
    direct=0
    upstream=0
    downstream=0
    security=0
    delay=0
    monitor=0
    version=''
    site=''
     
    def __init__(self, fn, na, ho, re):
        if na=='grif':
            na=fn
        self.fullname=fn
        self.name=na
        self.host=ho
        self.redirector=re
    
    def prnt(self, what):
        if (what>=0 and self.redirector!=what): return
        print '------------------------------------\nfullname:',self.fullname
        print 'redirector:', self.redirector, '\tname:', self.name, '\thost:', self.host
        print 'responds:', self.direct, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t security:', self.security, '\t delay:', self.delay, '\t monitored:', self.monitor
        


class redirector:
    def __init__(self, name, address):
        self.name=name
        self.address=address
        self.upstream=False
        self.downstream=False
        self.status=0
        self.version=''
        self.site=''
    def prnt(self):
        print 'redirector: ', self.name, '\taddress: ', self.address, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t status:', self.status

    

try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        print  s["name"],s["rc_site"], s["endpoint"], s["redirector"]["endpoint"]
        si=site(s["name"].lower(),s["rc_site"].lower(), s["endpoint"], s["redirector"]["endpoint"])
        sites.append(si)
except:
    print "Unexpected error:", sys.exc_info()[0]    
    

        
print 'Geting redirector list from AGIS...' 
try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_redirector_services/?json&state=ACTIVE", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        print s["name"], s["endpoint"]
        redirectors.append(redirector(s["name"],s["endpoint"]))
except:
    print "Unexpected error:", sys.exc_info()[0]    


class Command(object):
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
    
    def run(self, timeout):
        def target():
            print 'command started: ', self.cmd
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
        
        thread = threading.Thread(target=target)
        thread.start()
        
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode
    


for s in sites: s.prnt(-1) # print all
    

with open('checkAPs.sh', 'w') as f:
    for s in sites:
        logfile='checkAP_'+s.name+'.log'
        f.write('xrdfs '+s.host.replace('root://','')+' query stats a >'+logfile+' & \n')
    for r in redirectors:
        logfile='checkAP_'+r.name+'.log'  
        f.write('xrdfs '+r.address.replace('root://','')+' query stats a >'+logfile+' & \n')
        
    f.close()

#sys.exit(0)
print 'executing all of the xrds in parallel. 70s timeout.'
com = Command("source /afs/cern.ch/user/i/ivukotic/FAXtools/FAX_AP_status/checkAPs.sh")
com.run(60)
time.sleep(70)


print 'checking log files'


for s in sites:  # this is file to be asked for
    logfile='checkAP_'+s.name+'.log'
    print "parsing:", logfile
    try:
        tree = ET.parse(logfile)
        root = tree.getroot()
        atr=root.attrib
        print atr
        s.version=atr["ver"]
        s.site=atr["site"]
    except:
        print "something wrong in this one."
        
        
for s in redirectors:  # this is file to be asked for
    logfile='checkAP_'+s.name+'.log'
    print "parsing:", logfile
    try:
        tree = ET.parse(logfile)
        root = tree.getroot()
        atr=root.attrib
        print atr
        s.version=atr["ver"]
        s.site=atr["site"]
    except:
        print "something wrong in this one."

print '--------------------------------- Writing SEs for twiki ----------------------------'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiSitesStatus.log', 'w') as f: 
    f.write('| *name* | *address* | *version* | *site* |\n')
    for s in sites:
        f.write('| '+s.name+' | '+s.host+' | '+s.version+ ' | '+s.site+ '|\n')
    f.write("last update: "+datetime.datetime.utcnow().strftime("%A, %d. %B %Y %I:%M%p"))
    f.close()


print '--------------------------------- Writing redirectors for twiki ----------------------------'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiRedirectorsStatus.log', 'w') as fi:
    fi.write("| *name* | *address* | *version* | *site* |\n")
    try:
        for r in redirectors:
            fi.write('| '+r.name+' | '+r.address+' | '+r.version+ ' | '+r.site+ '|\n')
    except:
        print "Unexpected error:", sys.exc_info()[0]
    fi.write("last update: "+datetime.datetime.utcnow().strftime("%A, %d. %B %Y %I:%M%p"))
    fi.close()
    
