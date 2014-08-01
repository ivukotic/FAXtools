#!/usr/bin/env python
import sys
import stomp
import time, datetime
import json
import socket

from agisconf import agis

# getting downed sites
# unneded statuslist = agis.get_site_status(activity='DDMFT')

downtimes_ongoing = agis.list_downtimes(ongoing_time=datetime.datetime.utcnow())
downed=set()
for i in downtimes_ongoing:
     for en in range(len(downtimes_ongoing[i])):
          afs=downtimes_ongoing[i][en].affected_services
          if ('SRM' in afs or 'SRMv2' in afs):
               print "Affected site:", i, afs
               downed.add(i)

global messages
messages=[]

hostalias='dashb-test-mb.cern.ch'
s=socket.gethostbyname_ex(hostalias)
print 'aliases: ', s[2]
allhosts=[]
for a in s[2]:
    allhosts.append([(a, 6162)])

queue = '/queue/faxmon.topology'

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
    times=''
    delay=0
    def logpostfix(self):
        return '_'+self.times[:13].replace(' ','T')+'00.log' 

for host in allhosts:
# Connect to the stompserver, listen to the queue for 2 seconds, print the messages and disconnect
    try:                                                                                                                                                                                                                                        
        conn = stomp.Connection(host, use_ssl=True, ssl_key_file='/etc/grid-security/hostkey.pem', ssl_cert_file='/etc/grid-security/hostcert.pem')
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
                if l[0]=='siteName': s.name=l[1]
                if l[0]=='metricName': continue
                if l[0]=='metricStatus': s.status=int(l[1])
                if l[0]=='timestamp': s.times = l[1]
                if l[0]=='delay': s.delay = l[1] 
            if s.name in downed:
                s.status=999
            sites.append(s)        

print 'writing direct.json'

#site=' http://athena-infoioperformance.web.cern.ch/athena-infoIOperformance/logs/FAXconfiguration/'
site=' http://www.mwt2.org/ssb/'

f1 = open('direct.json','w')
for s in sites:
    js=s.times+' '+s.name
    log=s.name+'_to_'+s.name
    sta=' OK green'
    if not s.status&(1<<0): sta=' noDirect red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f1.write(js)
f1.close()        

print 'writing upstream.json'

f2 = open('upstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='upstreamFrom_'+s.name
    sta=' OK green'
    if not s.status&(1<<1): sta=' NoUpstreamRedirection red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f2.write(js)
f2.close()

print 'writing downstream.json'
   
f3 = open('downstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='downstreamTo_'+s.name
    sta=' OK green'
    if not s.status&(1<<2): sta=' NoFirstLevelRedirection red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f3.write(js)
f3.close()

print 'writing rucio.json'

f11 = open('rucio.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='rucio_'+s.name
    sta=' OK green'
    if not s.status&(1<<5): sta=' NoRucioNamesSupport red'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f11.write(js)
f11.close()


print 'writing security.json'

f4 = open('security.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='checkSecurity_'+s.name
    sta=' On green'
    if not s.status&(1<<3): sta=' Off yellow'
    if s.status==999: sta=' offline gray'
    js+=sta+site+log+s.logpostfix()+' \n'
    f4.write(js)
f4.close()

print 'writing delays.json'

f5 = open('delays.json','w')
for s in sites:
    js=s.times+' '+s.name
    log='checkDelays_'+s.name
    sta = s.delay +' green'
    if (float(s.delay)>1): sta = s.delay + ' yellow'
    if (float(s.delay)>10): sta = s.delay + ' blue'
    if s.status==999: sta='offline gray' 
    js+=' '+sta+site+log+s.logpostfix()+' \n'
    f5.write(js)
f5.close()


print 'writing mailing.json'

content={}
sits=agis.list_sites()
for s in sites:
    if s.status==999: continue
    msg=''
    lowerfour=s.status&7
    if lowerfour==7: continue
    if not lowerfour&(1<<0): msg+='Direct xrootd access not working. '
    #if not lowerfour&(1<<2): msg+='Data unreachable via parent redirector. '
    if not lowerfour&(1<<1): msg+='No upstream failover.'
    if not lowerfour&(1<<3): msg+='ATLAS role extension not enabled for access.'
    print s.name, msg
    for cloud,sit in sits.iteritems():
        for si in sit:
            if si.name.upper()!=s.name: continue
            if not cloud in content:
                content[cloud]=[]   
            content[cloud].append({si.name:msg})

f6 = open('mailing.json','w')
f6.write(json.dumps(content))
f6.close()

print 'writing monitoring.json'
ts=datetime.datetime.now()
ts=ts.replace(microsecond=0)
ts=ts.replace(second=0)
fr=str(ts-datetime.timedelta(0,5*3600)).replace(" ","+").replace(":","%3A")
to=str(ts).replace(" ","+").replace(":","%3A")
ur=" http://dashb-atlas-xrootd-transfers.cern.ch/dashboard/request.py/test-details.json?client=voatlas106.cern.ch&from_date="+fr+"&to_date="+to

f7 = open('monitoring.json','w')
for s in sites:
    js=s.times+' '+s.name
    sta=' On green'
    if not s.status&(1<<4): sta=' Off yellow'
    if s.status==999: sta=' offline gray'
    js+=sta+ur+'\n'
    f7.write(js)
f7.close()

print 'done.'
