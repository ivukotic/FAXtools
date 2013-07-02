#!/usr/bin/env python
import sys, time, urllib2, simplejson
from datetime import datetime, timedelta

DATE_FROM="2013-06-09"
DATE_TO="2013-06-10"
SRC_METRIC_ID=10096
linkadd="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?batch=1&time=custom&dateFrom="+DATE_FROM+"&dateTo="+DATE_TO+"&columnid="+str(SRC_METRIC_ID)

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
        inted=inte.total_seconds()/86400
        w=1-inted
        self.caverage = v*w+(1-w)*self.caverage
        self.average.append(self.caverage)
        
    def prnt(self):
        print 'source:', self.source,'\tdestination:',self.destination
        for v,t,a in zip(self.values, self.tim, self.average):
            print t, v, a, (v-a)/a
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
    

