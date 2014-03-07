#!/usr/bin/env python
import subprocess, threading
import os, sys, time
import pycurl, urllib2
import cStringIO

try: 
	import simplejson as json
except ImportError: 
	import json


interval=6 # in hours
limit=100 # jobs in the interval

FAXfailovers={}

class det:
    def __init__(self):
        self.FAXfinished=0
        self.FAXfailed=0
        self.FAXfiles=0
        self.FAXfsize=0
        self.FAXfilesNot=0
        self.FAXfsizeNot=0
    def toString(self):
        ret = "finished: "+str(self.FAXfinished)
        ret+= "\tfailed: "+str(self.FAXfailed)
        return ret+"\tdelivered using FAX - files: "+str(self.FAXfiles)+"\tsize: "+str(self.FAXfsize)


link="http://pandamon.cern.ch/fax/failover?hours="+str(interval)

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
    res=json.loads(js)
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
        
except json.scanner.JSONDecodeError:
    print "Decoding Error"
except:
    print "Unexpected error:", sys.exc_info()[0]
    
    
sites={};

class site:    

    def __init__(self, em, qu):        
        self.email=em
        self.queues=qu
        self.found=0
    
    def prnt(self):
        print 'emails:', self.email
        print 'queues:', self.queues


try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/site/query/list/?json&vo_name=atlas&state=ACTIVE", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        # print  s["name"], s["emailContact"], s["presources"]
        queues=[]
        for sit in s["presources"].itervalues():
            queues.extend(sit.keys())
        sites[s["name"]] = site( s["emailContact"].split(','), queues )
        
except:
    print "Unexpected error:", sys.exc_info()[0]    
    

# for s in sites: 
#     print '------------------------------------'
#     print s
#     sites[s].prnt()



for FFqueue, FFvalues in FAXfailovers.items():
    if FFvalues.FAXfinished + FFvalues.FAXfailed > limit:
        for Ss,Sd in sites.items():
            if FFqueue in Sd.queues:
                Sd.found+=1 

        
towrite={}
    
for Ss,Sd in sites.items():
    if Sd.found==0: continue
    sdict={}
    print "-------------------------------------"
    print Ss, Sd.email
    sdict["to"]=Sd.email
    sdict["subject"]="Unusually high number of jobs failing over to FAX at "+Ss
    sdict["body"]="Dear Site responsible(s),\n\n\tAn automated script found that unusually large number of jobs running at your site is using the failover-to-FAX mechanism. "
    sdict["body"]+="This kind of message is generated when more than "+str(limit)+" jobs of at least one of the queues failover to FAX during last "+str(interval)+" hours. "
    sdict["body"]+="Jobs that failed-over tried to get the job's input data in a regular way three times and failed. While a part (or even all) of these jobs finished successfully, your understanding of why this happened could make "+Ss+" even more efficient in the future.\n\n"
    sdict["body"]+="\tHere is a list of all the queues that had failed-over jobs:\n"
    print "All the queues from your site: "
    for sq in Sd.queues:
        for FFqueue, FFvalues in FAXfailovers.items():
            if sq!=FFqueue: continue
            print sq, FFvalues.toString()
            sdict["body"]+=sq+" \t "+FFvalues.toString()
    sdict["body"]+="\n\n\tFurther details can be found here: "+link
    towrite[Ss] = sdict
        
f1 = open('FAX_failover_mails.json','w')
f1.write(json.dumps(towrite))
f1.close()      
            

# print '--------------------------------- Writing SEs for twiki ----------------------------'
# with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiSitesStatus.log', 'w') as f: 
#     f.write('| *name* | *address* | *version* | *site* |\n')
#     for s in sites:
#         f.write('| '+s.name+' | '+s.host+' | '+s.version+ ' | '+s.site+ '|\n')
#     f.close()
# 
