#!/usr/bin/env python
import sys
import stomp
import time
import json

from agisconf import agis
from datetime import datetime

# getting downed sites
# unneded statuslist = agis.get_site_status(activity='DDMFT')
downtimes_ongoing = agis.list_downtimes(ongoing_time=datetime.utcnow())
downed=[]
for i in downtimes_ongoing:
     afs=downtimes_ongoing[i][0].affected_services
     if ('SRM' in afs): 
          print "Affected site:", i, afs
          downed.append(i.upper())

global messages
messages=[]

hosts=[('pilot.msg.cern.ch', 6163)]
queue = '/queue/fax.mon.topology'


class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message
    
    def on_message(self, headers, message):
        #print 'received a message %s' % message
        messages.append(message)
    

sites=[]
class site:
    name=''
    status=0
    times=0


# Connect to the stompserver, listen to the queue for 2 seconds, print the messages and disconnect
try:                                                                                                                                                                                                                                        
    conn = stomp.Connection(hosts)
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
            if l[0]=='siteName': s.name=l[1].upper()
            if l[0]=='metricName': continue
            if l[0]=='metricStatus': s.status=int(l[1])
            if l[0]=='timestamp': s.times = l[1] 
        if s.name in downed:
            s.status=999
        sites.append(s)        

print 'writing direct.json'

site=' http://athena-infoioperformance.web.cern.ch/athena-infoIOperformance/logs/FAXconfiguration/'

f1 = open('direct.json','w')
for s in sites:
    js=s.times+' '+s.name
    log=s.name.lower()+'_to_'+s.name.lower()
    sta=' OK green'
    if not s.status&(1<<0): sta=' noDirect red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+'.log \n'
    f1.write(js)
f1.close()        

print 'writing upstream.json'

f2 = open('upstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='upstreamFrom_'+s.name.lower()
    sta=' OK green'
    if not s.status&(1<<1): sta=' NoUpstreamRedirection red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+'.log \n'
    f2.write(js)
f2.close()

print 'writing downstream.json'
   
f3 = open('downstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='downstreamTo_'+s.name.lower()
    sta=' OK green'
    if not s.status&(1<<2): sta=' NoFirstLevelRedirection red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+'.log \n'
    f3.write(js)
f3.close()

print 'writing security.json'

f4 = open('security.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='checkSecurity_'+s.name.lower()
    sta=' On green'
    if not s.status&(1<<3): sta=' Off red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+'.log \n'
    f4.write(js)
f4.close()

print 'writing mailing.json'

content={}
sits=agis.list_sites()
for s in sites:
    if s.status==15 or s.status==999: continue
    msg=''
    if not s.status&(1<<0): msg+='Direct xrootd access not working. '
    if not s.status&(1<<2): msg+='Data unreachable via parent redirector. '
    if not s.status&(1<<1): msg+='No upstream failover.'
    if not s.status&(1<<3): msg+='Security disabled.'
    print s.name, msg
    for cloud,sit in sits.iteritems():
        for si in sit:
            if si.name.upper()!=s.name: continue
            if not cloud in content:
                content[cloud]=[]   
            content[cloud].append({si.name:msg})

f4 = open('mailing.json','w')
f4.write(json.dumps(content))
f4.close()

print 'done.'
