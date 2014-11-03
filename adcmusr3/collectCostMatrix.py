#!/usr/bin/env python
import sys
import stomp, ssl
import time

from agisconf import agis
from datetime import datetime
import socket

import logging
logging.basicConfig(level=logging.DEBUG)

statuslist = agis.get_site_status(activity='DDMFT')
downtimes_ongoing = agis.list_downtimes(ongoing_time=datetime.utcnow())


outputdir=sys.argv[1]
print 'output will be stored in:', outputdir

global messages
messages=[]

hostalias='dashb-mb.cern.ch'
s=socket.gethostbyname_ex(hostalias)
print 'aliases: ', s[2]
allhosts=[]
for a in s[2]:
    allhosts.append([(a, 61123)])
queue = '/queue/faxmon.costMatrix'


class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message
    
    def on_message(self, headers, message):
        #print 'received a message %s' % message
        messages.append(message)


class sites:
    def __init__(self):
        self.siteD=[]
    def prnt(self):
        return str(len(self.siteD))
    def addSite(self,sit):
        for s in self.siteD:
            if s.fr==sit.fr and s.to==sit.to: 
                print 'adding measurement to ', s.prnt()
                s.addMeasurement(sit.rates[0], sit.timestamps[0])
                return
        print 'appended site'
        self.siteD.append(sit)
  
class site:
    def __init__(self):
        self.rates=[]
        self.timestamps=[]
        self.fr='def'
        self.to='def'
    def prnt(self):
        return self.fr + '->' + self.to +"  "+str(len(self.rates))+ " rates. "
    def addMeasurement(self, rate, timestamp):
        self.rates.append(rate)
        self.timestamps.append(timestamp)    
    def getTime(self):
        return self.timestamps[0]
    def getRate(self):
        if len(self.rates)==0: return -1
        avRate=0
        for r in self.rates:
            avRate+=r
        return avRate/len(self.rates)


allSites=sites()

logFile=sys.argv[2]
lf = open(logFile, 'w')

# Connect to all of the  stompservers, listen to the queue for 2 seconds, print the messages and disconnect
for host in allhosts: 
    try:
        conn = stomp.Connection(host, use_ssl=True, ssl_version=ssl.PROTOCOL_TLSv1, ssl_key_file='/afs/cern.ch/user/a/adcmusr3/.globus/Request2014/hostkey.pem', ssl_cert_file='/afs/cern.ch/user/a/adcmusr3/.globus/Request2014/hostcert.pem')
        conn.set_listener('MyConsumer', MyListener())
        conn.start()
        conn.connect()
        conn.subscribe(destination = queue, ack = 'auto', id="1", headers = {})    
        time.sleep(2)  
        conn.disconnect()
    finally:
        for message in messages:
            s=site()
            message=message.split('\n')
            for l in message:
                # print l
                l=l.split(": ")
                if len(l)<2: continue
                l[1]=l[1].strip()
                print l[0],l[1],"\t",
                lf.write(l[0]+" "+l[1]+" \t")
                if l[0]=='site_from': s.fr=l[1]
                if l[0]=='site_to': s.to=l[1]
                if l[0]=='metricName': continue
                if l[0]=='rate': s.rates.append(float(l[1]))
                if l[0]=='timestamp': s.timestamps.append( l[1] )
            print 
            lf.write("\n")
            allSites.addSite(s)
        messages=[]        

lf.close()

f1 = open(outputdir+'/cost.data','w')
f2 = open(outputdir+'/costsource.data','w')
f3 = open(outputdir+'/costdestination.data','w')
for s in allSites.siteD:
    rat="{0:.2f}".format(s.getRate())
    print s.prnt()+"  AvRate: " + rat,;  print s.rates 
    js=s.getTime()+' '+s.fr+'_to_'+s.to+' '+rat+' '
    jsou=s.getTime()+' '+s.fr+'_to_'+s.to+' '+s.fr+' white http://www.mwt2.org/ssb/'+logFile+'\n'
    jdes=s.getTime()+' '+s.fr+'_to_'+s.to+' '+s.to+' white http://www.mwt2.org/ssb/'+logFile+'\n'
    if s.getRate()<0.1:
        js+='red'
    if s.getRate()<1.0 and s.getRate()>0.1:
        js+='yellow'
    if s.getRate()>1.0 and s.getRate()<10.0:
        js+='green'
    if s.getRate()>10:
        js+='blue'
    js+=' http://www.mwt2.org/ssb/'+logFile+'\n'
    f1.write(js)
    f2.write(jsou)
    f3.write(jdes)
f1.close()        
f2.close()
f3.close()

print '---------------------------------------------------------------------------'
