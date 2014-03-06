#!/usr/bin/env python
import subprocess, threading
import os, sys, time
import pycurl, urllib2
import cStringIO

try: 
	import simplejson as json
except ImportError: 
	import json


hours=2

FAXfailovers={}

class det:
    def __init__(self):
        self.FAXfinished=0
        self.FAXfailed=0
        self.FAXfiles=0
        self.FAXfsize=0
        self.FAXfilesNot=0
        self.FAXfsizeNot=0
        self.TOTfinished=0
        self.TOTfailed=0
    def toString(self):
        ret = "finished: "+str(self.FAXfinished)+"/"+str(self.TOTfinished)
        ret+= "\tfailed: "+str(self.FAXfailed)+"/"+str(self.TOTfailed)
        return ret+"\tfiles: "+str(self.FAXfiles)+"\tfsize: "+str(self.FAXfsize)+"\tfilesNOT: "+str(self.FAXfilesNot)+"\tfsizeNOT: "+str(self.FAXfsizeNot)


link="http://pandamon.cern.ch/fax/failover?hours="+str(hours)

buf = cStringIO.StringIO()

c = pycurl.Curl()
c.setopt(c.URL, link)
# c.setopt(c.VERBOSE, True)
c.setopt(c.WRITEFUNCTION, buf.write)
c.perform()
c.close()
js= buf.getvalue()
buf.close()

try:
    res=simplejson.loads(js)
    res=res["pm"][0]['json']['info']
    for r in res:
        # print r
        sn=r[2].split(":")[1]
        if sn not in FAXfailovers:
            FAXfailovers[sn] = det()
        d=FAXfailovers[sn]
        if r[3]=='finished':
            d.FAXfinished+=1
        if r[3]=='failed':
            d.FAXfailed+=1
        d.FAXfiles+=r[5]
        d.FAXfilesNot+=r[6]
        d.FAXfsize+=r[7]
        d.FAXfsizeNot+=r[8]
        
except simplejson.scanner.JSONDecodeError:
    print "Decoding Error"
except:
    print "Unexpected error:", sys.exc_info()[0]
    
    
# sites=[]; # each site contains [name, host, redirector]
# 
# class site:    
#     name=''
#     fullname=''
#     host=''
#     redirector=''
#     direct=0
#     upstream=0
#     downstream=0
#     security=0
#     delay=0
#     monitor=0
#     version=''
#     site=''
#      
#     def __init__(self, fn, na, ho, re):
#         if na=='grif':
#             na=fn
#         self.fullname=fn
#         self.name=na
#         self.host=ho
#         self.redirector=re
#     
#     def prnt(self, what):
#         if (what>=0 and self.redirector!=what): return
#         print '------------------------------------\nfullname:',self.fullname
#         print 'redirector:', self.redirector, '\tname:', self.name, '\thost:', self.host
#         print 'responds:', self.direct, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t security:', self.security, '\t delay:', self.delay, '\t monitored:', self.monitor
#         
# 
# 
# 
# try:
#     req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
#     opener = urllib2.build_opener()
#     f = opener.open(req)
#     res=json.load(f)
#     for s in res:
#         print  s["name"],s["rc_site"], s["endpoint"], s["redirector"]["endpoint"]
#         si=site(s["name"].lower(),s["rc_site"].lower(), s["endpoint"], s["redirector"]["endpoint"])
#         sites.append(si)
# except:
#     print "Unexpected error:", sys.exc_info()[0]    
#     
# 
# for s in sites: s.prnt(-1) # print all
#     
# 
#         
# 
# print '--------------------------------- Writing SEs for twiki ----------------------------'
# with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiSitesStatus.log', 'w') as f: 
#     f.write('| *name* | *address* | *version* | *site* |\n')
#     for s in sites:
#         f.write('| '+s.name+' | '+s.host+' | '+s.version+ ' | '+s.site+ '|\n')
#     f.close()
# 
