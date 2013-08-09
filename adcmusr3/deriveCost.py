#!/usr/bin/env python
import sys, time, urllib2, simplejson
from datetime import date, datetime, timedelta

days=6

DATE_FROM=date.today()-timedelta(days)
DATE_TO=date.today()+timedelta(1)
# SRC_METRIC_ID=10096 # my metric
SRC_METRIC_ID=10091 # FAX metric from sonar

linkadd="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?batch=1&time=custom&dateFrom="+str(DATE_FROM)+"&dateTo="+str(DATE_TO)+"&columnid="+str(SRC_METRIC_ID)
SmoothingFactor=0.5

print linkadd

class link:
    
    source=''
    destination=''
    
    def __init__(self, s, d, v, t):
        self.source=s
        self.destination=d
        self.values=[]
        self.values.append(v)
        self.average=[]
        self.average.append(v)
        self.caverage=v
        self.tim=[]
        self.tim.append(datetime.strptime(t,'%Y-%m-%dT%H:%M:%S'))
        self.ctime=datetime.strptime(t,'%Y-%m-%dT%H:%M:%S')
        
    def addValues(self, v, t ):
        self.values.append(v)
        ti=datetime.strptime(t,'%Y-%m-%dT%H:%M:%S')
        self.tim.append(ti)
        inte=ti-self.ctime
        self.ctime=ti
        inted=inte.total_seconds()/86400
        w=(1-inted)*SmoothingFactor
        self.caverage = v*w+(1-w)*self.caverage
        self.average.append(self.caverage)
        
    def prnt(self):
        print 'source:', self.source,'\tdestination:',self.destination
        for t,v,a in zip(self.tim, self.values,  self.average):
            print t,"\t", v,"\t", a,"\t", (v-a)/a*100,"%"
        print '\n-----------------------------------------------------------'
         
links={}
    
try:
    req = urllib2.Request(linkadd, None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=simplejson.load(f)
    if res["csvdata"] is None:
        print 'no data. returned:'
        print res
    data=res["csvdata"]
    print 'total lines:',len(data)
    for s in data:
        # print s
        VO=s['VOName']
        val=s['Value']
        sid=s['SiteId']
        tim=s['Time']
        etim=s['EndTime']
        # print sid, VO, val, tim, etim
        
        if sid in links.keys():
            links[sid].addValues(val,tim)
        else:
            links[sid]=link(VO.split("_to_")[0], VO.split("_to_")[1], val, tim)
except:
    print "Unexpected error:", sys.exc_info()[0]

print 'total links:', len(links)
    
for l in links.keys():
    # print l, links[l].source, links[l].destination, len(links[l].values)  ,links[l].values[0],links[l].values[1]
    links[l].prnt()
    

print "************************** publishing results **************************"

import pycurl
import cStringIO
buf = cStringIO.StringIO()

c = pycurl.Curl()
c.setopt(pycurl.SSLCERT, './usercert.pem')
c.setopt(pycurl.SSLKEY, './userkey.pem')
c.setopt(pycurl.SSLCERTPASSWD, 'Leptir3!')
c.setopt(pycurl.HEADER, 1)
c.setopt(pycurl.SSL_VERIFYHOST, 0)
c.setopt(pycurl.SSLVERSION, 3)
c.setopt(pycurl.SSL_VERIFYPEER, 0)
c.setopt(c.URL, 'https://atlas-agis-api-dev.cern.ch:2831/request/site/update/link/')
#c.setopt(c.URL, 'http://atlas-agis.cern.ch/agis/request/site/update/link/')
coun=0
ds="data=["
for l in links.keys():
    if coun>0: ds+=', '
    ds+='{ "psnravgval":1, "snrlrgdev":1, "snrlrgval":1, "snrmeddev":1, "snrmedval":1, "snrsmldev":1, "snrsmlval":1,'
    ds+=' "src":"'+links[l].source+'", "dst":"'+links[l].destination+'", "xrdcpval":'+str(links[l].caverage)+'}'
    coun+=1
    #if coun>500: break
data=ds+"]"
print data


c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, data)
c.setopt(c.VERBOSE, True)
c.setopt(c.WRITEFUNCTION, buf.write)
c.perform()
c.close()
print buf.getvalue()
buf.close()
