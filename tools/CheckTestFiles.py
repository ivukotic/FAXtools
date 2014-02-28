#!/usr/bin/env python

import subprocess, threading, os, sys,time
import datetime, random
import urllib2

try:
	import simplejson as json
except ImportError:
	import json

        
class Command(object):
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
    
    def run(self, timeout):
        def target():
            print 'command started: ', self.cmd
            self.process = subprocess.Popen(self.cmd, shell=True)
            return self.process.communicate()[0]
        
        thread = threading.Thread(target=target)
        thread.start()
        
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode
    
    
    

print 'Geting site list from AGIS...'


sites={}


try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/site/query/list/?json", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        print  s["name"],s["rc_site"], s["endpoint"], s["tier_level"], s["ddmendpoints"]
        # si=site(s["name"],s["rc_site"], s["endpoint"], s["tier_level"], s["ddmendpoints"])
        sites[s["name"]]=[s["rc_site"], s["endpoint"], s["tier_level"], s["ddmendpoints"]]
except:
    print "Unexpected error:", sys.exc_info()[0]


sitesToCheck=[]
for i in (1,len(sys.argv)-1):
    stc=sys.argv[i]
    found=0
    for s in sites:
        if stc==s.name:
            sitesToCheck.append(stc)
            found=1
    if not found:
        print 'Unrecognized site name:', stc
        
print 'Sites To check:', sitesToCheck


# read file list file
sitesToCheck=[]
with open("ALL_SITES.txt", 'r') as f:
    lines=f.readlines()
    for l in lines:
        sitesToCheck.append(l.rstrip())
        # print l
        
# for s in sites:
#     if s.name not in sitesToCheck: continue
#     sname=s.name.upper()
#     for f in files:
#         nfile=f.replace("root://fax.mwt2.org",s.host).replace("MWT2",sname)
#         print nfile
#         c='root -q -b "list.C(\\"'+nfile+'\\")" >> '+sname+'.log'
#         com = Command(c)    
#         if (com.run(60)!=0):
#             s.fails+=1
#         else:
#             s.successes+=1
#     print sname, "\tsuccesses:",s.successes,"\t\tfails:" ,s.fails,"\t\tsuccess rate: ",s.successes*100./(s.successes+s.fails)," %"
        
