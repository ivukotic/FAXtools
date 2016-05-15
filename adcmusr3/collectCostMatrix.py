#!/usr/bin/env python
import sys
import stomp, ssl
import time

from agisconf import agis
from datetime import datetime
import socket

from elasticsearch import Elasticsearch
from elasticsearch import helpers

import logging

debug=False

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.ERROR)

statuslist = agis.get_site_status(activity='DDMFT')
downtimes_ongoing = agis.list_downtimes(ongoing_time=datetime.utcnow())


outputdir=sys.argv[1]
if debug:
    print 'output will be stored in:', outputdir

global messages
messages=[]

hostalias='dashb-mb.cern.ch'
queue = '/queue/faxmon.costMatrix'

d = datetime.now()
ind = "faxcost-" + str(d.year) + "." + str(d.month).zfill(2) 
        
s=socket.gethostbyname_ex(hostalias)
if debug: 
    print 'aliases: ', s[2]

allhosts=[]
for a in s[2]:
    allhosts.append([(a, 61123)])



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
                if debug: print 'adding measurement to ', s.prnt()
                s.addMeasurement(sit.rates[0], sit.timestamps[0])
                return
        if debug: print 'appended site'
        self.siteD.append(sit)

class site:
    def __init__(self):
        self.rates=[]
        self.timestamps=[]
        self.fr='def'
        self.to='def'
    def prnt(self):
        return 'source:'+self.fr + ',destination:' + self.to +",measurements:"+str(len(self.rates))
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
allData = []
logFile=sys.argv[2]
lf = open(logFile, 'w')

# Connect to all of the  stompservers, listen to the queue for 2 seconds, print the messages and disconnect
for host in allhosts: 
    try:
        # /afs/cern.ch/user/a/adcmusr3/.globus/adcmusr3_20151009_EXPIRE-20161112/hostkey.pem
        # /afs/cern.ch/user/a/adcmusr3/.globus/adcmusr3_20151009_EXPIRE-20161112/hostcert.pem
        conn = stomp.Connection(host, use_ssl=True, ssl_version=ssl.PROTOCOL_TLSv1, ssl_key_file='/afs/cern.ch/user/a/adcmusr3/.globus/adcmusr3_20151009_EXPIRE-20161112/hostkey.pem', ssl_cert_file='/afs/cern.ch/user/a/adcmusr3/.globus/adcmusr3_20151009_EXPIRE-20161112/hostcert.pem')
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
            data = {
                '_index': ind,
                '_type': 'rate'
            }
            for l in message:
                # print l
                l=l.split(": ")
                if len(l)<2: continue
                l[1]=l[1].strip()
                if debug: print l[0],l[1],"\t",
                lf.write(l[0]+" "+l[1]+" \t")
                if l[0]=='site_from': 
                    s.fr=l[1]
                    data['source']=l[1]
                if l[0]=='site_to': 
                    s.to=l[1]
                    data['destination']=l[1]
                if l[0]=='metricName': continue
                if l[0]=='rate': 
                    s.rates.append(float(l[1]))
                    data['rate']=float(l[1])
                if l[0]=='timestamp': 
                    s.timestamps.append( l[1] )
                    data['timestamp']=l[1].replace(' ','T')
            if debug: print 
            lf.write("\n")
            allSites.addSite(s)
            allData.append(data)
        messages=[]        

lf.close()

es = Elasticsearch([{'host':'cl-analytics.mwt2.org', 'port':9200}])
es1 = Elasticsearch([{'host':'es-atlas.cern.ch', 'port':9202}], ,http_auth=('es-atlas', 'pass'))
try:
    res = helpers.bulk(es, allData, raise_on_exception=True)
    print "inserted:",res[0], '\tErrors:',res[1]
except helpers.BulkIndexError as e:
    print "indexing error: ", e
except:
    print 'Something seriously wrong happened in idexing to UC step. ', sys.exc_info()[0]

try:
    res = helpers.bulk(es1, allData, raise_on_exception=True)
    print "inserted:",res[0], '\tErrors:',res[1]
except helpers.BulkIndexError as e:
    print "indexing error: ", e
except:
    print 'Something seriously wrong happened in idexing to CERN step. ', sys.exc_info()[0]

f1 = open(outputdir+'/cost.data','w')
f2 = open(outputdir+'/costsource.data','w')
f3 = open(outputdir+'/costdestination.data','w')
for s in allSites.siteD:
    rat="{0:.2f}".format(s.getRate())
    print s.prnt()+",AvRate:" + rat;
    if debug:
        print s.rates 
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
