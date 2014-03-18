#!/usr/bin/env python
import subprocess, threading, os, sys
import urllib2
import datetime

try: import simplejson as json
except ImportError: import json

class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print 'command started: ', self.cmd
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode



SRC = 'RAL-LCG2'
DST = 'MWT2'

timeout=3600

url="http://ivukotic.web.cern.ch/ivukotic/FTS/getFTS.asp?"
url+="SRC="+SRC
url+="&DST="+DST
print url

response = urllib2.urlopen(url)
html = response.read()
print html
response.close()  

v=html.split(',')
tid=v[0]
fn=v[1]
fsize=v[2]

com = Command('/usr/bin/time -f "real: %e" ls ' + fn + '  ')
com.run(timeout)


#uploading transfer
url="http://ivukotic.web.cern.ch/ivukotic/FTS/addFAX.asp?"
url+="TID="+tid
url+="&FAXTIME="+str(100)

print url
    
req = urllib2.Request(url)
opener = urllib2.build_opener()
f = opener.open(req)
