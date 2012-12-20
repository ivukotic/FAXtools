#!/usr/bin/env python
import subprocess, threading, os, sys, cx_Oracle,time
import stomp, logging, datetime, ConfigParser

logging.basicConfig()

config = ConfigParser.ConfigParser()
config.read("neet.cfg")
HOST = config.get("Connection", "HOST")
PORT = int(config.get("Connection", "PORT"))
QUEUE = config.get("Connection", "QUEUE")


def send (message):
    """ Send message by stomp protocols.
    @param message: the message being sent
    
    """  
    conn = stomp.Connection([(HOST,PORT)])
    conn.start()
    conn.connect()
    
    conn.send(message,destination=QUEUE, ack='auto')
    
    try:
       conn.disconnect()
    except Exception:
        'Exception on disconnect'


timeouts=300
sleeps=250

sites=[]; # each site contains [name, host, redirector]

class site:    
    name=''
    host=''
    redirector=''
    direct=0
    redirects=0
    comm1=''
     
    def __init__(self, na, ho, re):
        self.name=na
        self.host=ho
        self.redirector=re
    
    def prnt(self, what):
        if (what>=0 and self.redirector!=what): return
        print '\tredirector:', self.redirector, '\tname:', self.name, '\thost:', self.host, '\tresponds:', self.direct, '\t redirects:', self.redirects
    

print 'Geting site list from AGIS...' 

import urllib2,simplejson

try:
    req = urllib2.Request("http://atlas-agis-api-0.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=simplejson.load(f)
    for s in res:
        print  s["rc_site"], s["endpoint"], s["redirector"]["endpoint"]
        si=site(s["rc_site"].lower(), s["endpoint"], s["redirector"]["endpoint"])
        sites.append(si)
except:
    print "Unexpected error:", sys.exc_info()[0]    


        

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
    


for s in sites: s.prnt(-1) # print all
print 'creating scripts to execute'
    
print "================================= CHECK I =================================================="
    
with open('toExecute.sh', 'w') as f: # first check that site itself gives it's own file
    for s in sites:
        logfile=s.name+'_to_'+s.name+'.log'
        lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.'+s.name+'-1M'
        s.comm1='xrdcp -f -np -d 1 '+s.host+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
        f.write(s.comm1)
    f.close()

#sys.exit(0)
print 'executing all of the xrdcps in parallel. 5 min timeout.'
com = Command("source toExecute.sh")    
com.run(timeouts)
time.sleep(sleeps)


print 'checking log files'

# checking which sites gave their own file directly
for s in sites:  # this is file to be asked for
    logfile=s.name+'_to_'+s.name+'.log'
    with open(logfile, 'r') as f:
        lines=f.readlines()
        succ=False
        for l in lines:
            # print l
            if l.startswith(" BytesSubmitted"):
                succ=True
                break
        if succ==True:
            print logfile, "works"
            s.direct=1
        else:
            print logfile, "problem"
        send ('siteName: '+ s.name + '\nmetricName: FAXprobe1\nmetricStatus: '+str(s.direct)+'\ntimestamp: '+datetime.datetime.now().isoformat(' ')+'EOT\n') 
            
for s in sites: s.prnt(0)  #print only real sites

sys.exit(0)

print "================================= CHECK II ================================================="

with open('checkRedirection.sh', 'w') as f: # ask good sites for unexisting file
    for s in sites:
        if s.direct==0: continue
        logfile='redirectFrom_'+s.name+'.log'
        lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.unexisting-1M'
        comm='xrdcp -f -np -d 1 root://'+s.host+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
        f.write(comm)            
    f.close()
    
print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
com = Command("source checkRedirection.sh")    
com.run(timeouts)
time.sleep(sleeps)

alllinks=set()

for s in sites:
    if s.direct==0: continue
    logfile='redirectFrom_'+s.name+'.log'
    with open(logfile, 'r') as f:
        print logfile
        lines=f.readlines()        
        reds=[]
        for l in lines:
            if l.count("Received redirection")>0:
                red=l[l.find("[")+1 : l.find("]")]
                reds.append(red.split(':')[0])
        links=[]
        print 'redirections:',reds
        if len(reds)==0:
            s.redirects=0
            print 'redirection does not work'
        else:    
            s.redirects=1
            links.append( [s.host, reds[0] ] )
            alllinks.add( s.siteid * 10000 + getSiteID(reds[0]) )
            lr=len(reds)
            for c in range(lr-1):
                links.append([reds[c],reds[c+1]])
                alllinks.add( getSiteID(reds[c]) * 10000 + getSiteID(reds[c+1]) )
            print 'links: ', links



print "================================= CHECK III ================================================"

with open('checkUpDown.sh', 'w') as f: # ask global redirectors for files belonging to good sites
    for red in [16,17]:        
        for s in sites:
            if s.redirector>0 or s.direct==0: continue
            logfile='checkUpDown_'+getHost(red)+'_to_'+s.name+'.log'
            lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.'+s.name+'-1M'
            comm='xrdcp -f -np -d 1 root://'+getHost(red)+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
            f.write(comm)            
    f.close()

print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
com = Command("source checkUpDown.sh")    
com.run(timeouts)
time.sleep(sleeps)



for d in [16,17]:        
    for s in sites:
        if s.redirector>0 or s.direct==0: continue
        logfile='checkUpDown_'+getHost(d)+'_to_'+s.name+'.log'
        with open(logfile, 'r') as f:
            print 'Checking file: ', logfile
            lines=f.readlines()
            succ=False
            reds=[]
            for l in lines:
                if l.startswith(" BytesSubmitted"):
                    succ=True
            if succ==False: 
                print 'Did not work.' 
                continue                
            print 'OK'
            reds=[]
            for l in lines:
                if l.count("Received redirection")>0:
                    red=l[l.find("[")+1 : l.find("]")]
                    reds.append(red.split(':')[0])
            links=[]
            print 'redirections:',reds
            if len(reds)==0:
                s.redirects=0
                print 'redirection does not work'
            else:    
                s.redirects=1
                links.append( [getHost(d), reds[0] ] )
                print d, reds[0], d * 10000 + getSiteID(reds[0])
                alllinks.add( d * 10000 + getSiteID(reds[0]) )
                lr=len(reds)
                for c in range(lr-1):
                    links.append([reds[c],reds[c+1]])
                    if getSiteID(reds[c])==0 or getSiteID(reds[c+1])==0: continue
                    
                    print getSiteID(reds[c]), getSiteID(reds[c+1]), getSiteID(reds[c]) * 10000 + getSiteID(reds[c+1])
                    alllinks.add( getSiteID(reds[c]) * 10000 + getSiteID(reds[c+1]) )
                print 'links: ', links
                
for i in alllinks:
    s=int(round(i/10000))
    d=int(i-round(i/10000)*10000)
    if s==d:
        print 'source and destination the same. skip'
        continue
    if getHost(s)==0 or getHost(d)==0: continue
    print 'uploading -  s:',s,'\td:',d,'\tfile from:',getHost(s),"\t was asked from:",getHost(d)
        
