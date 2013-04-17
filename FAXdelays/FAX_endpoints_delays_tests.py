#!/usr/bin/env python
import subprocess, threading, os, sys,time
import logging, datetime

timeouts=300
sleeps=250

DTS='//atlas/dq2/user/flegger/XXX/user.flegger.XXX.data12_8TeV.00212172.physics_Muons.merge.NTUP_SMWZ.f479_m1228_p1067_p1141_tid01007411_00/'
DTSFNS=[
    'NTUP_SMWZ.01007411._000122.XXX.root.2',
    'NTUP_SMWZ.01007411._000091.XXX.root.1',
    'NTUP_SMWZ.01007411._000053.XXX.root.1',
    'NTUP_SMWZ.01007411._000103.XXX.root.1',
    'NTUP_SMWZ.01007411._000083.XXX.root.1',
    'NTUP_SMWZ.01007411._000057.XXX.root.1',
    'NTUP_SMWZ.01007411._000108.XXX.root.1',
    'NTUP_SMWZ.01007411._000121.XXX.root.2',
    'NTUP_SMWZ.01007411._000114.XXX.root.1',
    'NTUP_SMWZ.01007411._000033.XXX.root.1',
    'NTUP_SMWZ.01007411._000128.XXX.root.1',
    'NTUP_SMWZ.01007411._000059.XXX.root.1',
    'NTUP_SMWZ.01007411._000022.XXX.root.1',
    'NTUP_SMWZ.01007411._000041.XXX.root.1',
    'NTUP_SMWZ.01007411._000065.XXX.root.1',
    'NTUP_SMWZ.01007411._000136.XXX.root.1',
    'NTUP_SMWZ.01007411._000077.XXX.root.1',
    'NTUP_SMWZ.01007411._000134.XXX.root.2',
    'NTUP_SMWZ.01007411._000019.XXX.root.1',
    'NTUP_SMWZ.01007411._000007.XXX.root.1',
    'NTUP_SMWZ.01007411._000010.XXX.root.2',
    'NTUP_SMWZ.01007411._000003.XXX.root.1',
    'NTUP_SMWZ.01007411._000046.XXX.root.1',
    'NTUP_SMWZ.01007411._000111.XXX.root.2',
    'NTUP_SMWZ.01007411._000036.XXX.root.1',
    'NTUP_SMWZ.01007411._000097.XXX.root.1',
    'NTUP_SMWZ.01007411._000069.XXX.root.1',
    'NTUP_SMWZ.01007411._000092.XXX.root.1',
    'NTUP_SMWZ.01007411._000025.XXX.root.2',
    'NTUP_SMWZ.01007411._000120.XXX.root.2',
    'NTUP_SMWZ.01007411._000098.XXX.root.1',
    'NTUP_SMWZ.01007411._000084.XXX.root.1',
    'NTUP_SMWZ.01007411._000055.XXX.root.1',
    'NTUP_SMWZ.01007411._000116.XXX.root.2',
    'NTUP_SMWZ.01007411._000101.XXX.root.1',
    'NTUP_SMWZ.01007411._000135.XXX.root.1',
    'NTUP_SMWZ.01007411._000020.XXX.root.1',
    'NTUP_SMWZ.01007411._000006.XXX.root.1',
    'NTUP_SMWZ.01007411._000137.XXX.root.1',
    'NTUP_SMWZ.01007411._000021.XXX.root.1',
    'NTUP_SMWZ.01007411._000079.XXX.root.1',
    'NTUP_SMWZ.01007411._000011.XXX.root.1',
    'NTUP_SMWZ.01007411._000031.XXX.root.1',
    'NTUP_SMWZ.01007411._000087.XXX.root.1',
    'NTUP_SMWZ.01007411._000026.XXX.root.1',
    'NTUP_SMWZ.01007411._000089.XXX.root.1',
    'NTUP_SMWZ.01007411._000052.XXX.root.1',
    'NTUP_SMWZ.01007411._000071.XXX.root.1',
    'NTUP_SMWZ.01007411._000024.XXX.root.2',
    'NTUP_SMWZ.01007411._000030.XXX.root.1',
    'NTUP_SMWZ.01007411._000110.XXX.root.1',
    'NTUP_SMWZ.01007411._000001.XXX.root.1',
    'NTUP_SMWZ.01007411._000112.XXX.root.1',
    'NTUP_SMWZ.01007411._000130.XXX.root.1',
    'NTUP_SMWZ.01007411._000117.XXX.root.1',
    'NTUP_SMWZ.01007411._000067.XXX.root.1',
    'NTUP_SMWZ.01007411._000002.XXX.root.1',
    'NTUP_SMWZ.01007411._000138.XXX.root.1',
    'NTUP_SMWZ.01007411._000040.XXX.root.1',
    'NTUP_SMWZ.01007411._000047.XXX.root.1',
    'NTUP_SMWZ.01007411._000074.XXX.root.1',
    'NTUP_SMWZ.01007411._000124.XXX.root.1',
    'NTUP_SMWZ.01007411._000133.XXX.root.1',
    'NTUP_SMWZ.01007411._000023.XXX.root.2',
    'NTUP_SMWZ.01007411._000056.XXX.root.1',
    'NTUP_SMWZ.01007411._000075.XXX.root.1',
    'NTUP_SMWZ.01007411._000037.XXX.root.1',
    'NTUP_SMWZ.01007411._000060.XXX.root.1',
    'NTUP_SMWZ.01007411._000042.XXX.root.1',
    'NTUP_SMWZ.01007411._000038.XXX.root.1',
    'NTUP_SMWZ.01007411._000118.XXX.root.2',
    'NTUP_SMWZ.01007411._000016.XXX.root.1',
    'NTUP_SMWZ.01007411._000015.XXX.root.2',
    'NTUP_SMWZ.01007411._000123.XXX.root.1',
    'NTUP_SMWZ.01007411._000062.XXX.root.1',
    'NTUP_SMWZ.01007411._000099.XXX.root.1',
    'NTUP_SMWZ.01007411._000078.XXX.root.1',
    'NTUP_SMWZ.01007411._000082.XXX.root.1',
    'NTUP_SMWZ.01007411._000100.XXX.root.1',
    'NTUP_SMWZ.01007411._000058.XXX.root.1',
    'NTUP_SMWZ.01007411._000064.XXX.root.1',
    'NTUP_SMWZ.01007411._000085.XXX.root.1',
    'NTUP_SMWZ.01007411._000068.XXX.root.1',
    'NTUP_SMWZ.01007411._000017.XXX.root.1',
    'NTUP_SMWZ.01007411._000109.XXX.root.1',
    'NTUP_SMWZ.01007411._000032.XXX.root.1',
    'NTUP_SMWZ.01007411._000095.XXX.root.1',
    'NTUP_SMWZ.01007411._000105.XXX.root.1',
    'NTUP_SMWZ.01007411._000043.XXX.root.1',
    'NTUP_SMWZ.01007411._000119.XXX.root.2',
    'NTUP_SMWZ.01007411._000073.XXX.root.1',
    'NTUP_SMWZ.01007411._000129.XXX.root.1',
    'NTUP_SMWZ.01007411._000072.XXX.root.1',
    'NTUP_SMWZ.01007411._000094.XXX.root.1',
    'NTUP_SMWZ.01007411._000081.XXX.root.1',
    'NTUP_SMWZ.01007411._000008.XXX.root.1',
    'NTUP_SMWZ.01007411._000093.XXX.root.1',
    'NTUP_SMWZ.01007411._000061.XXX.root.1',
    'NTUP_SMWZ.01007411._000048.XXX.root.1',
    'NTUP_SMWZ.01007411._000029.XXX.root.1',
    'NTUP_SMWZ.01007411._000131.XXX.root.1',
    'NTUP_SMWZ.01007411._000009.XXX.root.1',
    'NTUP_SMWZ.01007411._000013.XXX.root.2',
    'NTUP_SMWZ.01007411._000034.XXX.root.1',
    'NTUP_SMWZ.01007411._000104.XXX.root.1',
    'NTUP_SMWZ.01007411._000090.XXX.root.1',
    'NTUP_SMWZ.01007411._000102.XXX.root.2',
    'NTUP_SMWZ.01007411._000044.XXX.root.1',
    'NTUP_SMWZ.01007411._000014.XXX.root.1',
    'NTUP_SMWZ.01007411._000076.XXX.root.2',
    'NTUP_SMWZ.01007411._000012.XXX.root.2',
    'NTUP_SMWZ.01007411._000049.XXX.root.1',
    'NTUP_SMWZ.01007411._000028.XXX.root.2',
    'NTUP_SMWZ.01007411._000045.XXX.root.1',
    'NTUP_SMWZ.01007411._000070.XXX.root.1',
    'NTUP_SMWZ.01007411._000106.XXX.root.1',
    'NTUP_SMWZ.01007411._000005.XXX.root.1',
    'NTUP_SMWZ.01007411._000080.XXX.root.1',
    'NTUP_SMWZ.01007411._000125.XXX.root.1',
    'NTUP_SMWZ.01007411._000066.XXX.root.1',
    'NTUP_SMWZ.01007411._000018.XXX.root.1',
    'NTUP_SMWZ.01007411._000127.XXX.root.1',
    'NTUP_SMWZ.01007411._000063.XXX.root.1',
    'NTUP_SMWZ.01007411._000096.XXX.root.1',
    'NTUP_SMWZ.01007411._000086.XXX.root.1',
    'NTUP_SMWZ.01007411._000107.XXX.root.1',
    'NTUP_SMWZ.01007411._000035.XXX.root.1',
    'NTUP_SMWZ.01007411._000050.XXX.root.1',
    'NTUP_SMWZ.01007411._000088.XXX.root.1',
    'NTUP_SMWZ.01007411._000004.XXX.root.1',
    'NTUP_SMWZ.01007411._000027.XXX.root.2',
    'NTUP_SMWZ.01007411._000126.XXX.root.1',
    'NTUP_SMWZ.01007411._000039.XXX.root.1',
    'NTUP_SMWZ.01007411._000132.XXX.root.1',
    'NTUP_SMWZ.01007411._000113.XXX.root.1',
    'NTUP_SMWZ.01007411._000054.XXX.root.1',
    'NTUP_SMWZ.01007411._000051.XXX.root.1',
    'NTUP_SMWZ.01007411._000115.XXX.root.2'
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
for s in sites:
    cou=cou+1
    if not cou==sys.argv[1]: continue
    print 'site no: ',cou
    for fn in DTSFNS:
        logfile='delaysTo_'+s.name+'_'+fn+'.log'
        lookingFor = (DTS+fn).replace('XXX',s.name.upper())
        s.comm1='xrdcp -f -np -d 1 '+s.host+lookingFor+' /dev/null >& '+logfile+'  \n'
        com = Command(s.comm1)
        com.run(120)
    time.sleep(240)

sys.exit(0)
# print 'executing all of the xrdcps in parallel. 5 min timeout.'
# com = Command("source checkDelays.sh")    
# com.run(timeouts)
# time.sleep(sleeps)
# 
# 
# print 'checking log files'
# 
# # checking which sites gave their own file directly
# for s in sites:  # this is file to be asked for
#     if s.name.count('MWT2')==0: continue
#     logfile='delaysTo_'+s.name+'.log'
#     with open(logfile, 'r') as f:
#         lines=f.readlines()
#         succ=False
#         for l in lines:
#             # print l
#             if l.count("Read: Hole in the cache:")>0:
#                 succ=True
#                 break
#         if succ==True:
#             print logfile, "works"
#             s.direct=1
#         else:
#             print logfile, "problem"
#             
# for s in sites: s.prnt(0)  #print only real sites
# 
# #sys.exit(0)
# 
# print 'checking log files'
# 
# for s in sites: s.prnt(0)  #print only real sites
# 
# for s in sites:  
#     if s.direct==0: continue
#     logfile='delaysTo_'+s.name+'.log'
#     with open(logfile, 'r') as f:
#         lines=f.readlines()
#         for l in lines:
#             if l.count("requested")>0:
#                 print l
#     