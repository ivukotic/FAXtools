#!/usr/bin/env python
import urllib2
import datetime

try: import simplejson as json
except ImportError: import json

ur      ='http://dashb-atlas-data.cern.ch/dashboard/request.py/details.json?state=COPIED&limit=5000'
activity='&activity=6'
dest    ='&dst_site=%22MWT2%22'
dtto=datetime.datetime.utcnow()
dto     =  '&to_date='+str(dtto).replace(':','%3A') .replace(' ','T').split('.')[0]
interval = datetime.timedelta(minutes=200)
dtfr=dtto-interval
dfrom   ='&from_date='+str(dtfr).replace(':','%3A') .replace(' ','T').split('.')[0]
ur=ur+activity+dest+dfrom+dto

req = urllib2.Request(ur)
opener = urllib2.build_opener()
f = opener.open(req)
sj = json.load(f)

details=sj["details"]

# print len(details)

class transfer:
    def __init__(self, ac, src, dst, dur, siz, fn ):
        self.activity=ac
        self.src=src
        self.dst=dst
        self.duration=dur
        self.size=siz
        self.fn=fn
    def toString(self):
        return 'activity:' + str(self.activity) + '\tsrc:' + self.src + '\tdst:' + self.dst + '\tt:' + str(self.duration) + 's \t'+self.fn + '\t' + str(self.size)+'\t'+str(self.size/1024/1024/self.duration)+'MB/s'

transfers=[]

for d in details:
    rfn=d["src_surl"].split('rucio/')[1]
    sfn=rfn.split("/")
    t=transfer(d["activity"],d["src_site"],d["dst_site"],d["duration"],d["fsize"],sfn[0]+':'+sfn[3])
    print t.toString()
    transfers.append(d)
    
    #uploading transfer
    url="http://ivukotic.web.cern.ch/ivukotic/FTS/addFTS.asp?"
    url+="SRC="+t.src
    url+="&DST="+t.dst
    url+="&FN="+t.fn
    url+="&FSIZE="+str(t.size)
    url+="&FTSTIME="+str(t.duration)
    
    print url
    
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    # print f
    # break
    
print len(transfers)