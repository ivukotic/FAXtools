#!/usr/bin/env python
import subprocess, threading, os, sys,time
import logging, datetime,random

timeouts=300
sleeps=250

DTS='//atlas/rucio/1'
DTSFNS=[
    'data12_8TeV:NTUP_EMBLHIM.01233147._000005.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000008.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000010.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000017.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000029.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000037.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000039.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000055.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000056.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000057.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000061.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000074.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000090.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000099.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000105.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000110.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000005.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000008.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000010.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000017.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000029.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000037.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000039.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000055.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000056.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000057.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000061.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000074.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000090.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000099.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000105.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000110.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000001.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000002.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000003.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000004.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000021.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000022.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000023.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000024.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000025.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000026.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000027.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000028.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000030.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000031.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000032.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000100.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000101.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000102.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000103.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000104.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000106.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000107.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000108.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000109.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000058.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000059.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000061.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000062.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000063.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000064.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000065.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000066.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000067.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000068.root.1',
    'data12_8TeV:NTUP_EMBLHIM.01233147._000069.root.1'
]

# from random import choice
# DTSFN=choice(DTSFNS)

sites=[]; # each site contains [name, host, redirector]

class site:    
    name=''
    fullname=''
    host=''
    redirector=''
    direct=0
    upstream=0
    downstream=0
    security=0
    comm1=''
     
    def __init__(self, fn, na, ho, re):
        if na=='grif':
            na=fn
        self.fullname=fn
        self.name=na
        self.host=ho
        self.redirector=re
    
    def prnt(self, what):
        if (what>=0 and self.redirector!=what): return
        print 'fullname:',self.fullname,'\tredirector:', self.redirector, '\tname:', self.name, '\thost:', self.host, '\tresponds:', self.direct, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t security:', self.security
    
    def status(self):
       s=0
       s=s|(self.security<<3)
       s=s|(self.downstream<<2)
       s=s|(self.upstream<<1)
       s=s|(self.direct<<0)
       return s



print 'Geting site list from AGIS...' 

import urllib2,simplejson

try:
    req = urllib2.Request("http://atlas-agis-api-0.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=simplejson.load(f)
    for s in res:
        print  s["name"],s["rc_site"], s["endpoint"], s["redirector"]["endpoint"]
        si=site(s["name"].lower(),s["rc_site"].lower(), s["endpoint"], s["redirector"]["endpoint"])
        sites.append(si)
except:
    print "Unexpected error:", sys.exc_info()[0]    


        

class Command(object):
    
    def __init__(self, cmd, foreground=False):
        self.cmd = cmd
        self.process = None
        self.f=foreground
    
    def run(self, timeout):
        def target():
            print 'command started: ', self.cmd
            self.process = subprocess.Popen(self.cmd, shell=True)
            if (self.f): self.process.communicate()
        
        thread = threading.Thread(target=target)
        thread.start()
        
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode
    




for s in sites: s.prnt(-1) # print all
print 'creating scripts to execute'
    
print "================================= CHECK I =================================================="

cou=0
skip=0
for s in sites:
    cou=cou+1
    print cou, s.name
    if not cou==int(sys.argv[1]): continue
    cou2=0
    for fn in DTSFNS:
        cou2=cou2+1
        if cou2<skip: continue
        if cou2>skip+int(sys.argv[2]): continue
        logfile='delaysTo_'+s.name+'_'+fn+'.log'
        lookingFor = (DTS+fn).replace('XXX',s.name.upper())#  +'_inexistent_'+str(random.randint(0,100000))
        s.host='uct2-s6.uchicago.edu:1096'
        s.comm1='/usr/bin/time -f"real: %e" xrd '+s.host.replace('root://','')+' existfile '+lookingFor+' >& '+logfile+'  \n'
        print s.comm1
        com = Command(s.comm1)
        com.run(120)
    
sys.exit(0)
