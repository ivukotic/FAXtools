#!/usr/bin/env python
import os, sys, time
from  datetime import datetime
from datetime import timedelta
try: import simplejson as json
except ImportError: import json

import urllib2

outputdir=sys.argv[1]
print 'output will be stored in:', outputdir

hours=5
cuthours=3
limtime=timedelta(0,cuthours*3600)
curtime=datetime.now()
cuttime=curtime-timedelta(0,hours*3600)

class site:
        direct=0
        directfails=timedelta(0)
        directworks=timedelta(0)
        upstream=0
        upstreamfails=timedelta(0)
        upstreamworks=timedelta(0)
        downstream=0
        downstreamfails=timedelta(0)
        downstreamworks=timedelta(0)
        monitoring=0
        monitoringfails=timedelta(0)
        monitoringworks=timedelta(0)
        lastReported=[0,0,0,0] # direct, upstream,downstream, monitoring. 0 - good news, 1 - bad news.
        def __init__(self,na,cl):
                self.name=na
		self.cloud=cl
		self.lastReported=[0,0,0,0]
        def prn(self):
                print self.name, self.cloud
                print  "directfails: ",self.directfails,"/",self.direct
                print  "directworks: ",self.directworks
		print  "upstream: ",self.upstreamfails,"/",self.upstream
                print  "downstream: ",self.downstreamfails,"/",self.downstream
		print  "last reported: ",self.lastReported
        def mess(self):
                ret=''
                if self.directfails>limtime and self.direct==3:
			self.directfails-=timedelta(0,0,self.directfails.microseconds)
                        ret+="Failing to copy file from site during more than "+str(cuthours)+" in last "+str(hours)+" hours. "
                if self.upstreamfails>limtime and self.upstream==3:
			self.upstreamfails-=timedelta(0,0,self.upstreamfails.microseconds)
                        ret+="Failing to redirect upstream from site during more than "+str(cuthours)+" in last "+str(hours)+" hours. "
                if self.downstreamfails>limtime and self.downstream==3:
			self.downstreamfails-=timedelta(0,0,self.downstreamfails.microseconds)
                        ret+="Failing to respond to request from redirector during more than "+str(cuthours)+" in last "+str(hours)+" hours. "
                return ret



#direct
url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10083"
print url
try:
	response=urllib2.Request(url,None)
	opener = urllib2.build_opener()
	f = opener.open(response)
	data = json.load(f)
	data=data["csvdata"]
except:
    print "Unexpected error:", sys.exc_info()[0]

Sites=dict()
for si in data:
	n=si['VOName']
	if n not in Sites:
		s=site(n,si['Cloud'])
		Sites[n]=s
	st=datetime.strptime(si["Time"],'%Y-%m-%dT%H:%M:%S')
	et=datetime.strptime(si["EndTime"],'%Y-%m-%dT%H:%M:%S')
	if et<cuttime: continue  # throws away too early measurements
	if st<cuttime: st=cuttime # cuts to exact cutoff time 
	if et>curtime: # current state
		et=curtime
		Sites[n].direct=si['COLOR']
        if si['COLOR']==5: Sites[n].directworks+= (et - st)
	if si['COLOR']==3: Sites[n].directfails+= (et - st)

##upstream
url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10084"
print url
try:
        response=urllib2.Request(url,None)
        opener = urllib2.build_opener()
        f = opener.open(response)
        data = json.load(f)
        data=data["csvdata"]
except:
    print "Unexpected error:", sys.exc_info()[0]

for si in data:
        n=si['VOName']
        if n not in Sites:
                s=site(n,si['Cloud'])
                Sites[n]=s
        st=datetime.strptime(si["Time"],'%Y-%m-%dT%H:%M:%S')
        et=datetime.strptime(si["EndTime"],'%Y-%m-%dT%H:%M:%S')
        if et<cuttime: continue  # throws away too early measurements
        if st<cuttime: st=cuttime # cuts to exact cutoff time
        if et>curtime: # current state
                et=curtime
                Sites[n].upstream=si['COLOR']
        if si['COLOR']==5: Sites[n].upstreamworks+= (et - st)
        if si['COLOR']==3: Sites[n].upstreamfails+= (et - st)


##downstream
url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10085"
print url
try:
        response=urllib2.Request(url,None)
        opener = urllib2.build_opener()
        f = opener.open(response)
        data = json.load(f)
        data=data["csvdata"]
except:
    print "Unexpected error:", sys.exc_info()[0]

for si in data:
        n=si['VOName']
        if n not in Sites:
                s=site(n,si['Cloud'])
                Sites[n]=s
        st=datetime.strptime(si["Time"],'%Y-%m-%dT%H:%M:%S')
        et=datetime.strptime(si["EndTime"],'%Y-%m-%dT%H:%M:%S')
        if et<cuttime: continue  # throws away too early measurements
        if st<cuttime: st=cuttime # cuts to exact cutoff time
        if et>curtime: # current state
                et=curtime
                Sites[n].downstream=si['COLOR']
        if si['COLOR']==5: Sites[n].downstreamworks+= (et - st)
        if si['COLOR']==3: Sites[n].downstreamfails+= (et - st)


#monitoring


# lastReported
try:
	f1 = open(outputdir+'/LastReported.json','r')
        prev=json.load(f1)
        for c in prev:
		#print c, prev[c]
                if c in Sites:
			Sites[c].lastReported=prev[c]
        f1.close()
except:
	pass

# exit immediately in case too many direct access problems.
totFailedDirect=totFailedUp=totFailedDown=0
for sn,s in Sites.items():
	if s.direct==3: totFailedDirect+=1
        if s.upstream==3: totFailedUp+=1
        if s.downstream==3: totFailedDown+=1
if totFailedDirect>25 or totFailedUp>25 or totFailedDown>25:
    print "XXXXXXXXXXXXXXXX PROBLEM XXXXXXXXXXXXXXXXXX"
    print "X    A LARGE NUMBER OF FAILED TESTS       X"
    print "X    RECHECK MANUALY.                     X"
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    sys.exit(1)


alljson={}
clouds=dict() # for bad news
cleared=dict() # for cleared
alljson["failing"]=clouds
alljson["cleared"]=cleared
for sn,s in Sites.items():
	# if was previously red and now is green and it is green for > 3 hours pronounce cleared	
	if s.lastReported[0]==1 and s.directworks>limtime and s.direct==5:
		if s.cloud not in cleared:
			cleared[s.cloud]=dict()
		cleared[s.cloud][sn]="A direct access to files at site "+sn+" is now possible. "
		print "CLEARED direct!",sn, s.lastReported
		s.lastReported[0]=0

        if s.lastReported[1]==1 and s.upstreamworks>limtime and s.upstream==5:
                if s.cloud not in cleared:
                        cleared[s.cloud]=dict()
                if sn not in cleared[s.cloud]: cleared[s.cloud][sn]=''
		cleared[s.cloud][sn]+="An upstream redirection from site "+sn+" is now possible. "
                print "CLEARED upstream!",sn, s.lastReported
                s.lastReported[1]=0	

        if s.lastReported[2]==1 and s.downstreamworks>limtime and s.downstream==5:
                if s.cloud not in cleared:
                        cleared[s.cloud]=dict()
                if sn not in cleared[s.cloud]: cleared[s.cloud][sn]=''
                cleared[s.cloud][sn]+="A downstream redirection to site "+sn+" is now possible. "
                print "CLEARED downstream!",sn, s.lastReported
                s.lastReported[2]=0

	# if was previously green and now is red and it has been red for more than 3 hours pronounce blacklisted
	if s.lastReported[0]==0 and s.directfails>limtime and s.direct==3: 
		if s.cloud not in clouds:
			clouds[s.cloud]=dict()
		clouds[s.cloud][sn]="Failing to directly copy file from site during more than "+str(cuthours)+" in last "+str(hours)+" hours. "
		print "BLACKLISTED direct!", sn, s.lastReported
		s.lastReported[0]=1 

        if s.lastReported[1]==0 and s.upstreamfails>limtime and s.upstream==3:
                if s.cloud not in clouds:
                        clouds[s.cloud]=dict()
                if sn not in clouds[s.cloud]: clouds[s.cloud][sn]=''
                clouds[s.cloud][sn]+="Failing to redirect upstream from site during more than "+str(cuthours)+" in last "+str(hours)+" hours. "
                print "BLACKLISTED upstream!", sn, s.lastReported
                s.lastReported[1]=1

        if s.lastReported[2]==0 and s.downstreamfails>limtime and s.downstream==3:
                if s.cloud not in clouds:
                        clouds[s.cloud]=dict()
                if sn not in clouds[s.cloud]: clouds[s.cloud][sn]=''
                clouds[s.cloud][sn]+="Failing to access file via downstream redirection during more than "+str(cuthours)+" in last "+str(hours)+" hours. "
                print "BLACKLISTED downstream!", sn, s.lastReported
                s.lastReported[2]=1
print alljson

f1 = open(outputdir+'/LastReported.json','w')
towrite=dict()
for s in Sites.values():
	towrite[s.name]=s.lastReported 
f1.write(json.dumps(towrite))
f1.close()

f1 = open(outputdir+'/InstantMailing.json','w')
f1.write(json.dumps(alljson))
f1.close()

#for s in Sites.values():
#	s.prn()
