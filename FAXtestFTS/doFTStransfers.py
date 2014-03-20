#!/usr/bin/env python
import subprocess, threading, os, sys, time
import urllib2
from  datetime import datetime
from datetime import timedelta

try: import simplejson as json
except ImportError: import json

debug=1
SRC = 'ANY' # or 'ANY'
DST = 'MWT2'
timeout=3600

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



class site:
        def __init__(self,na):
                self.name=na
                self.direct=0
                self.endpoint=''
        def getEndpoint(self):
            if self.endpoint!='': return self.endpoint
            print "# looking up endpoint",self.name," address in AGIS..."
            try:
                url="http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD&rc_site="+self.name
                print url
                req = urllib2.Request(url, None)
                opener = urllib2.build_opener()
                f = opener.open(req, timeout=20)
                res=json.load(f)
                if debug: print "# found corresponding endpoint: ",res[0]["endpoint"]
                self.endpoint=res[0]["endpoint"]
                return self.endpoint
            except urllib2.HTTPError:
                print "# Can't connect to AGIS to get endpoint address."
                sys.exit(4)
            except:
                print "# Can't connect to AGIS to get endpoint address.", sys.exc_info()[0]
                sys.exit(41)
        def prn(self):
                print "#", self.name, "\tendpoint:",self.endpoint, "\tdirect: ",self.direct
                



print "# geting FAX endpoints information from SSB..."
url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10083"
try:
    response=urllib2.Request(url,None)
    opener = urllib2.build_opener()
    f = opener.open(response, timeout=20)
    data = json.load(f)
    data=data["csvdata"]
except urllib2.HTTPError:
        print "# Can't connect to SSB."
        sys.exit(2)
except:
    print "# Can't connect to SSB.", sys.exc_info()[0]
    sys.exit(21)

Sites=dict()

curtime=datetime.now()
cuttime=curtime-timedelta(0,5*3600)

for si in data:
        n=si['VOName']
        if n not in Sites:
                s=site(n)
                Sites[n]=s
        st= datetime(*(time.strptime(si["Time"], '%Y-%m-%dT%H:%M:%S')[0:6]))
        et= datetime(*(time.strptime(si["EndTime"], '%Y-%m-%dT%H:%M:%S')[0:6]))
        if et<cuttime: continue  # throws away too early measurements
        if st<cuttime: st=cuttime # cuts to exact cutoff time
        if et>curtime: # current state
                et=curtime
                Sites[n].direct=si['COLOR']

for s in Sites:
    Sites[s].prn()


url="http://ivukotic.web.cern.ch/ivukotic/FTS/getFTS.asp?"
url+="SRC="+SRC
url+="&DST="+DST
print url

while (True):
    response = urllib2.urlopen(url)
    html = response.read()
    print "got transfer:", html
    response.close()  

    v=html.split(',')
    tid=v[0]
    fn=v[1]
    fsize=v[2]
    source=v[3]

    if tid=='null': break
    
    endpoint=""
    if source not in Sites:
        print "site:",source, "not federated."
    else:
        if Sites[source].direct==5:
            endpoint=Sites[source].getEndpoint()
        else:
            print "site:",source,"in red, ATM."
            
    #com = Command('/usr/bin/time -f "real: %e" -a -o "logfile.txt" xrdcopy  -np -d 1 -f '+endpoint+'//atlas/rucio/'+ fn + ' /dev/null &> logfile.txt ')
    com = Command('/usr/bin/time -f "real: %e" -a -o "logfile.txt" xrdcp  -np -d 1 -f '+endpoint+'//atlas/rucio/'+ fn + ' /dev/null &> logfile.txt ')
    com.run(timeout)

    success=0
    with open('logfile.txt', 'r') as f:
        lines=f.readlines()
        for line in lines:
            if line.count("real:")>0 and success:
                rt=line.replace("real: ","")    
                #uploading transfer
                aurl="http://ivukotic.web.cern.ch/ivukotic/FTS/addFAX.asp?"
                aurl+="TID="+tid
                aurl+="&FAXTIME="+rt
                if debug: print aurl
                req = urllib2.Request(aurl)
                opener = urllib2.build_opener()
                f = opener.open(req)
            
            if line.count('BytesSubmitted=')>0:
                si=line.split()[0].split("=")[1]
                print si
                if si==fsize:
                    success=1

