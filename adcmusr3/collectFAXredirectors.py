#!/usr/bin/env python
import sys
import stomp
import time
import json
import socket

from agisconf import agis
from datetime import datetime

outputdir=sys.argv[1]
print 'output will be stored in:', outputdir

global messages
messages=[]

hostalias='dashb-test-mb.cern.ch'
s=socket.gethostbyname_ex(hostalias)
print 'aliases: ', s[2]
allhosts=[]
for a in s[2]:
    allhosts.append([(a, 61123)])

queue = '/queue/faxmon.redirectors'

class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message
    
    def on_message(self, headers, message):
        #print 'received a message %s' % message
        messages.append(message)
    

sites=[]
class site:
    name=''
    address=''
    status=0
    times=0
    def logpostfix(self):
        return '_'+self.times[:16].replace(' ','T').replace(':','')+'.log'

for host in allhosts:
# Connect to the stompserver, listen to the queue for 2 seconds, print the messages and disconnect
    try:
        conn = stomp.Connection(host, use_ssl=True, ssl_key_file='/afs/cern.ch/user/a/adcmusr3/.globus/Request2014/hostkey.pem', ssl_cert_file='/afs/cern.ch/user/a/adcmusr3/.globus/Request2014/hostcert.pem')
        conn.set_listener('MyConsumer', MyListener())
        conn.start()
        conn.connect()
        conn.subscribe(destination = queue, ack = 'auto', headers = {})    
        time.sleep(2)  
    finally:
        conn.disconnect()
        for message in messages:
            s=site()
            message=message.split('\n')
            for l in message:
                # print l
                l=l.split(": ")
                if len(l)<2: continue
                l[1]=l[1].strip()
                print l[0],l[1]
                if l[0]=='redirectorName': s.name=l[1].upper()
                if l[0]=='metricName': continue
                if l[0]=='address': s.address=l[1]
                if l[0]=='metricStatus': s.status=int(l[1])
                if l[0]=='timestamp': s.times = l[1]
            sites.append(s)        

print 'writing red_address.json'

#site=' http://athena-infoioperformance.web.cern.ch/athena-infoIOperformance/logs/FAXconfiguration/'
site=' http://www.mwt2.org/ssb/'

f1 = open(outputdir+'/red_address.json','w')
for s in sites:
    js=s.times+' '+s.name+' '+s.address
    if s.status&1: 
        js+=' gray'
    else:
        js+=' white'
    js+=site+' \n'
    f1.write(js)
f1.close()        

print 'writing red_upstream.json'

f2 = open(outputdir+'/red_upstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='checkRedirectorUpstream_'+s.name
    sta=' OK green'
    if s.status&4: sta=' NoUpstreamRedirection red'
    if s.status&1: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f2.write(js)
f2.close()

print 'writing red_downstream.json'
   
f3 = open(outputdir+'/red_downstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='checkRedirectorDownstream_'+s.name
    sta=' OK green'
    if s.status&2: sta=' NoDownstreamRedirection red'
    if s.status&1: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f3.write(js)
f3.close()


print 'writing red_mailing.json'

content={}
sits=agis.list_sites()
for s in sites:
    continue
    if s.status==15 or s.status==999: continue
    msg=''
    if not s.status&(1<<0): msg+='Direct xrootd access not working. '
    if not s.status&(1<<2): msg+='Data unreachable via parent redirector. '
    if not s.status&(1<<1): msg+='No upstream failover.'
    if not s.status&(1<<3): msg+='ATLAS role extension not enabled for access.'
    print s.name, msg
    for cloud,sit in sits.iteritems():
        for si in sit:
            if si.name.upper()!=s.name: continue
            if not cloud in content:
                content[cloud]=[]   
            content[cloud].append({si.name:msg})

f6 = open(outputdir+'/red_mailing.json','w')
f6.write(json.dumps(content))
f6.close()

print 'done.'
