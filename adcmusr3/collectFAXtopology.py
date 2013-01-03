#!/usr/bin/env python
import sys
import stomp
import time

global messages
messages=[]


class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message

    def on_message(self, headers, message):
        #print 'received a message %s' % message
        messages.append(message)

hosts=[('pilot.msg.cern.ch', 6163)]
queue = '/queue/fax.mon.topology'

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
    
    with open('FAXtopology.json','w') as f: 
        for message in messages:
            js=''
            message=message.split('\n')
            for l in message:
                # print l
                l=l.split(": ")
                if len(l)<2: continue
                l[1]=l[1].strip()
                print l[0],l[1]
                if l[0]=='siteName': js=capitalize(l[1])
                if l[0]=='metricName': continue
                if l[0]=='metricStatus': 
                    stat=l[1]
                    js+=' '+stat
                    if stat=='0': js+=' red'
                    if stat=='1' or stat=='2' or stat=='3': js+=' blue'
                    if stat=='4': js+=' green'
                if l[0]=='timestamp': js=l[1]+' '+js
            js+=' https://twiki.cern.ch/twiki/bin/viewauth/Atlas/MonitoringFax#ADC\n'
            f.write(js)
        f.close()
