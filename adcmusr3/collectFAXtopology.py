#!/usr/bin/env python
import sys
import stomp
import time

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
        sites.append(s)        


f1 = open('direct.json','w')
for s in sites:
    js=s.times+' '+s.name
    if s.status==0:
        js+=' noDirect red'
    else:
        js+=' OK green'
    js+=' https://twiki.cern.ch/twiki/bin/viewauth/Atlas/MonitoringFax#ADC\n'
    f1.write(js)
f1.close()        

f2 = open('upstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    if s.status==0 or s.status==3:
        js+=' NoFirstLevelRedirection red'
    else:
        js+=' OK green'
    js+=' https://twiki.cern.ch/twiki/bin/viewauth/Atlas/MonitoringFax#ADC\n'
    f2.write(js)
f2.close()
   
f3 = open('downstream.json','w')
for s in sites:
    js=s.times+' '+s.name
    if s.status==0 or s.status==2:
        js+=' NoUpstreamRedirection red'
    else:
        js+=' OK green'
    js+=' https://twiki.cern.ch/twiki/bin/viewauth/Atlas/MonitoringFax#ADC\n'
    f3.write(js)
f3.close()