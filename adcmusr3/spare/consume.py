import sys
import stomp
import time

global messages
messages=[]


class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message

    def on_message(self, headers, message):
        print 'received a message %s' % message
        messages.append(message)

hosts=[('pilot.msg.cern.ch', 6163)]

try:
    queue = sys.argv[1]
except KeyError:
    print("Please specify the queue (e.g. /queue/project_scorpio)")

# Connect to the stompserver, listen to the queue for 2 seconds, print the messages and disconnect
try:                                                                                                                                                                                                                                        
    conn = stomp.Connection(hosts)
    conn.set_listener('MyConsumer', MyListener())
    conn.start()
    conn.connect()
    conn.subscribe(destination = queue, ack = 'auto', headers = {})    
    time.sleep(2)  
   
    print ('Main has following messages:')
    for message in messages:
        print (message)

finally:
    conn.disconnect()

