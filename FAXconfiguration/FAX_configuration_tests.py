#!/usr/bin/env python
import subprocess, threading, os, sys, time
import stomp, logging, datetime, ConfigParser, random
import urllib, urllib2
from random import shuffle

try: import simplejson as json
except ImportError: import json

logging.basicConfig()

config = ConfigParser.ConfigParser()
config.read("neet.cfg")
HOST = config.get("Connection", "HOST")
PORT = int(config.get("Connection", "PORT"))
USER = config.get("Connection", "USER")
PASS = config.get("Connection", "PASS")
QUEUE = config.get("Connection", "QUEUE")
REDIRECTORSQUEUE = config.get("Connection","REDIRECTORSQUEUE")

def send (message):
    """ Send message by stomp protocols.
    @param message: the message being sent
    
    """  
    conn = stomp.Connection([(HOST,PORT)],USER,PASS)
    conn.start()
    conn.connect()
    conn.send(message,destination=QUEUE, ack='auto')    
    try:
       conn.disconnect()
    except Exception:
        'Exception on disconnect'

def sendRed (message):
    conn = stomp.Connection([(HOST,PORT)],USER,PASS)
    conn.start()
    conn.connect()
    conn.send(message,destination=REDIRECTORSQUEUE, ack='auto')
    try:
       conn.disconnect()
    except Exception:
        'Exception on disconnect'


timeouts=300
sleeps=250

sites=[]; # each site contains [name, host, redirector]
redirectors=[]

class site:    
    name=''
    fullname=''
    host=''
    redirector=''
    direct=0
    upstream=0
    downstream=0
    security=0
    delay=0
    monitor=0
    comm1=''
    
    def __init__(self, fn, na, ho, re):
        if na=='GRIF':
            na=fn
        self.fullname=fn
        self.lname=na.lower()
        self.name=na
        self.host=ho
        self.redirector=re
        # self.rucio=0
    
    def prnt(self, what):
        if (what>=0 and self.redirector!=what): return
        print '------------------------------------\nfullname:',self.fullname
        print 'redirector:', self.redirector, '\tname:', self.name, '\thost:', self.host
        print 'responds:', self.direct, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t security:', self.security, '\t delay:', self.delay, '\t monitored:', self.monitor
    
    def status(self):
       s=0
       # s=s|(self.rucio<<5)
       s=s|(self.monitor<<4)
       s=s|(self.security<<3)
       s=s|(self.downstream<<2)
       s=s|(self.upstream<<1)
       s=s|(self.direct<<0)
       return s

class redirector:
    def __init__(self, name, address):
        self.name=name
        self.address=address
        self.upstream=False
        self.downstream=False
        self.status=0
    def prnt(self):
        print 'redirector: ', self.name, '\taddress: ', self.address, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t status:', self.status

print 'Geting site list from AGIS...' 



try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        print  s["name"],s["rc_site"], s["endpoint"], s["redirector"]["endpoint"]
        si=site(s["name"],s["rc_site"], s["endpoint"], s["redirector"]["endpoint"])
        sites.append(si)
except:
    print "Unexpected error:", sys.exc_info()[0]    
    

        




print 'Geting redirector list from AGIS...' 
try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_redirector_services/?json&state=ACTIVE", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        print s["name"], s["endpoint"]
        redirectors.append(redirector(s["name"],s["endpoint"]))
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
    

dsNAMEpref='user.ivukotic.xrootd.'
fnNAMEpref='/user.ivukotic.xrootd.'
workingDir='/afs/cern.ch/user/i/ivukotic/FAXtools/FAXconfiguration/'
OKmessage='Read: Hole in the cache: offs=0, len=1048576'
ts=datetime.datetime.now()
logpostfix=ts.strftime("_%Y-%m-%dT%H%M")+'.log'
redstring=' - 2>&1 >/dev/null | cat >'

print "================================= CHECK DIRECT =================================================="
    
with open('checkDirect.sh', 'w') as f: # first check that site itself gives it's own file
    for s in sites:
        logfile=s.name+'_to_'+s.name+logpostfix
        lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'-1M'
        s.comm1='xrdcp -f -np -d 1 '+s.host+lookingFor+redstring+logfile+' & \n'
        f.write('echo "command executed:\n ' + s.comm1 + '" >> ' + logfile + '\n')
        f.write('echo "========================================================================" >> ' + logfile + '\n')
        f.write(s.comm1)
    f.close()

#sys.exit(0)
print 'executing all of the xrdcps in parallel. 5 min timeout.'
com = Command("source " + workingDir + "checkDirect.sh")    
com.run(timeouts)
time.sleep(sleeps)


print 'checking log files'

# checking which sites gave their own file directly
for s in sites:  # this is file to be asked for
    logfile=s.name+'_to_'+s.name+logpostfix
    with open(logfile, 'r') as f:
        lines=f.readlines()
        succ=False
        for l in lines:
            # print l
            if l.count(OKmessage)>0:
                succ=True
                break
        if succ==True:
            print logfile, "works"
            s.direct=1
        else:
            print logfile, "problem"
            
for s in sites: s.prnt(0)  #print only real sites

#sys.exit(0)

print "================================= CHECK UPSTREAM ================================================="

with open('checkUpstream.sh', 'w') as f: # ask good sites for unexisting file
    for s in sites:
        if s.direct==0: continue
        logfile='upstreamFrom_'+s.name+logpostfix
        lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'unexisting-1M'
        comm='xrdcp -f -np -d 1 '+s.host+lookingFor+redstring+logfile+' & \n'
        f.write('echo "command executed:\n ' + comm + '" >> ' + logfile + '\n')
        f.write('echo "========================================================================" >> ' + logfile + '\n')
        f.write(comm)            
    f.close()
    
print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
com = Command("source " + workingDir + "checkUpstream.sh")    
com.run(timeouts)
time.sleep(sleeps)


for s in sites:
    if s.direct==0: continue
    logfile='upstreamFrom_'+s.name+logpostfix
    with open(logfile, 'r') as f:
        print logfile
        lines=f.readlines()        
        reds=[]
        for l in lines:
            if l.count("Received redirection")>0:
                red=l[l.find("[")+1 : l.find("]")]
                reds.append(red.split(':')[0])
        print 'redirections:',reds
        if s.redirector.split(':')[0]  in reds:
            s.upstream=1
            print 'redirection works'
        else:    
            s.upstream=0
            print 'redirection does not work'

#sys.exit(0)
print "================================= CHECK DOWNSTREAM ================================================"

with open('checkDownstream.sh', 'w') as f: # ask global redirectors for files belonging to good sites
    for s in sites:
        if s.direct==0: continue
        logfile='downstreamTo_'+s.name+logpostfix
        lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'-1M'
        comm='xrdcp -f -np -d 1 root://'+s.redirector+lookingFor+redstring+logfile+' & \n'
        f.write('echo "command executed:\n ' + comm + '" >> ' + logfile + '\n')
        f.write('echo "========================================================================" >> ' + logfile + '\n')
        f.write(comm)            
    f.close()

print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
com = Command("source " + workingDir + "checkDownstream.sh")    
com.run(timeouts)
time.sleep(sleeps)

for s in sites:
    if s.direct==0: continue
    logfile='downstreamTo_'+s.name+logpostfix
    with open(logfile, 'r') as f:
        print 'Checking file: ', logfile
        lines=f.readlines()
        succ=False
        reds=[]
        for l in lines:
            if l.count(OKmessage)>0:
                succ=True
                s.downstream=1
        if succ==False: 
            print 'Did not work.'
            s.downstream=0 
            continue                
        print 'OK'
                
                

print "================================= CHECK DELAYS ================================================"

with open('checkDelays.sh', 'w') as f: 
    for s in sites:
        if s.direct==0: continue
        logfile='checkDelays_'+s.name+logpostfix
        lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'-10M'
        s.comm1='/usr/bin/time -f"real: %e" xrdfs '+s.host.replace('root://','')+' locate -r '+lookingFor+' 2>>'+logfile+' & \n'
        f.write('echo "command executed:\n ' + s.comm1 + '" >> ' + logfile + '\n')
        f.write('echo "========================================================================" >> ' + logfile + '\n')
        f.write(s.comm1)
    f.close()

#sys.exit(0)
print 'executing all of the xrd lookups in parallel. 1 min timeout.'
com = Command("source " + workingDir + "checkDelays.sh")
com.run(60)
time.sleep(sleeps)


print 'checking log files'

# checking sites delays
for s in sites:
    if s.direct==0: continue
    logfile='checkDelays_'+s.name+logpostfix
    with open(logfile, 'r') as f:
        lines=f.readlines()
        for l in lines:
            # print l
            if l.startswith("real:"):
                s.delay=float(l.split(":")[1])
                print s.name+': '+str(s.delay)
                break

              
                
print "================================= CHECK REDIRECTOR DOWNSTREAM ================================================"
                
with open('checkRedirectorDownstream.sh', 'w') as f:
    for r in redirectors:
        logfile='checkRedirectorDownstream_'+r.name.upper()+logpostfix
        thereIsUnderlayingWorkingSite=False
        for s in sites:
            if s.direct==0 or s.downstream==0: continue
            if s.redirector==r.address \
               or (r.name=='XROOTD_atlas-xrd-us' and s.redirector.count('usatlas')>0) \
               or (r.name=='XROOTD_atlas-xrd-eu' and s.redirector.count('cern.ch')>0):
                lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'-1M'
                comm='xrdcp -f -np -d 1 root://'+r.address+lookingFor+redstring+logfile+' & \n'
                f.write('echo "command executed:\n ' + comm + '" >> ' + logfile + '\n')
                f.write('echo "========================================================================" >> ' + logfile + '\n')
                f.write(comm)
                thereIsUnderlayingWorkingSite=True
                break
        if not thereIsUnderlayingWorkingSite:
            r.status|=1 # can not check downstream
            print 'Will not be checking downstream redirection to:',r.name
    f.close()

#sys.exit(0)
print 'executing all of the xrdcps  in parallel. 5 min timeout.'
com = Command("source " + workingDir + "checkRedirectorDownstream.sh")
com.run(timeouts)
time.sleep(sleeps)


print 'checking log files'

for r in redirectors:
    if r.status&1: continue
    logfile='checkRedirectorDownstream_'+r.name.upper()+logpostfix
    with open(logfile, 'r') as f:
        print 'Checking file: ', logfile
        lines=f.readlines()
        succ=False
        for l in lines:
            if l.count(OKmessage)>0:
                succ=True
                r.downstream=True
        if succ==False: 
            print 'Did not work.'
            r.status|=2               
        print 'OK'

                
                
                
print "================================= CHECK REDIRECTOR UPSTREAM ================================================"

                
with open('checkRedirectorUpstream.sh', 'w') as f:
    for r in redirectors:
        logfile='checkRedirectorUpstream_'+r.name.upper()+logpostfix
        thereIsOverlayingWorkingSite=False
        rsites=sites
        shuffle(rsites)
        for s in rsites:
            if s.direct==0 or s.downstream==0: continue
            if ( s.redirector.count('usatlas')!=r.address.count('usatlas') ):
                lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'-1M'
                comm='xrdcp -f -np -d 1 root://'+r.address+lookingFor+redstring+logfile+' & \n'
                f.write('echo "command executed:\n ' + comm + '" >> ' + logfile + '\n')
                f.write('echo "========================================================================" >> ' + logfile + '\n')
                f.write(comm)
                thereIsOverlayingWorkingSite=True
                break
        if not thereIsOverlayingWorkingSite:
            r.status|=1 # can not check upstream
    f.close()

#sys.exit(0)
print 'executing all of the xrdcps  in parallel. 5 min timeout.'
com = Command("source " + workingDir + "checkRedirectorUpstream.sh")
com.run(timeouts)
time.sleep(sleeps)


print 'checking log files'
for r in redirectors:
    if r.status&1: continue
    logfile='checkRedirectorUpstream_'+r.name.upper()+logpostfix
    with open(logfile, 'r') as f:
        print 'Checking file: ', logfile
        lines=f.readlines()
        succ=False
        for l in lines:
            if l.count(OKmessage)>0:
                succ=True
                r.upstream=True
        if succ==False: 
            print 'Did not work.'
            r.status|=4               
        print 'OK'



print "================================= CHECK X509 ================================================"

with open('checkSecurity.sh', 'w') as f: 
    f.write('export KRB5CCNAME=/nocredentials \n')
    f.write('rm -f /tmp/x509* \n') #deletes all existing proxies
    #creates a proxy without ATLAS VO role
    f.write('voms-proxy-init -cert /afs/cern.ch/user/i/ivukotic/.globus/usercert_slac.pem -key /afs/cern.ch/user/i/ivukotic/.globus/userkey_slac.pem -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt \n')
    for s in sites:
        if s.direct==0: continue
        logfile='checkSecurity_'+s.name+logpostfix
        # lookingFor = dsNAMEpref+s.lname+fnNAMEpref+s.lname+'-1M'
        lookingFor = '//atlas/rucio/user/ivukotic:user.ivukotic.xrootd.'+s.lname+'-1M'
        s.comm1='xrdcp -f -np -d 1 '+s.host+lookingFor+redstring+logfile+' & \n'
        f.write('echo "command executed:\n ' + s.comm1 + '" >> ' + logfile + '\n')
        f.write('echo "========================================================================" >> ' + logfile + '\n')
        f.write(s.comm1)
    f.close()

#sys.exit(0)
print 'executing all of the xrdcps in parallel. 5 min timeout.'
com = Command("source " + workingDir + "checkSecurity.sh")
com.run(timeouts)
time.sleep(sleeps)


print 'checking log files'

# checking which sites gave their own file directly
for s in sites:  # this is file to be asked for
    if s.direct==0: continue
    logfile='checkSecurity_'+s.name+logpostfix
    with open(logfile, 'r') as f:
        lines=f.readlines()
        succ=False
        for l in lines:
            # print l
            if l.count(OKmessage)>0:
                succ=True
                break
        if succ==True:
            print logfile, "security does not work."
            s.security=0
        else:
            s.security=1
            print logfile, "security works."

for s in sites: s.prnt(0)  #print only real sites



    
print "================================= CHECK MONITORING =================================================="
    
print 'Geting info from Dashboard ...' 
ts1=datetime.datetime.now()
ts1=ts1.replace(microsecond=0)
ts1=ts1.replace(second=0)
fr=str(ts1-datetime.timedelta(0,5*3600)).replace(" ","+").replace(":","%3A")
to=str(ts1).replace(" ","+").replace(":","%3A")
try:
    ur="http://dashb-atlas-xrootd-transfers.cern.ch/dashboard/request.py/test-details.json?client=voatlas106.cern.ch&from_date="+fr+"&to_date="+to
    req = urllib2.Request(ur, None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    res=res["testDetails"]
    for m in res:
        #print m
        if m['server_site'].count("MWT2"):
            m['server_site']="MWT2"
        found=0
        for s in sites:
            if s.lname==m['server_site'].lower():
                s.monitor=1
                found=1
        if not found:
            print "can't connect this record with any site:\n", m
except:
    print "Unexpected error:", sys.exc_info()[0]    





print '--------------------------------- Uploading site results ---------------------------------'
ts=ts.replace(microsecond=0)

for s in sites:
    send ('siteName: '+ s.name + '\nmetricName: FAXprobe1\nmetricStatus: '+str(s.status())+'\ndelay: '+str(s.delay)+'\ntimestamp: '+ts.isoformat(' ')+'\n')      


print '--------------------------------- Uploading redirector results ---------------------------------'
for r in redirectors:
    sendRed ('redirectorName: '+ r.name + '\nmetricName: FAXprobe2\naddress: '+r.address+'\nmetricStatus: '+str(r.status)+'\ntimestamp: '+ts.isoformat(' ')+'\n')      


print '--------------------------------- Writing SEs for twiki ----------------------------'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiSites.log', 'w') as f: 
    f.write('| *status* | *name* | *address* |\n')
    for s in sites:
        lin=''
        if s.direct==0: 
            lin+='| %ICON{led-red}% | '
        else:
            lin+='| %ICON{led-green}% | '
        f.write(lin+s.name+' | '+s.host+' |\n')
    f.close()


print '--------------------------------- Writing redirectors for twiki ----------------------------'
with open('/afs/cern.ch/user/i/ivukotic/www/logs/FAXconfiguration/tWikiRedirectors.log', 'w') as fi:
    fi.write("| *status* | *Site* | *Address* |\n")
    try:
        for r in redirectors:
            l=''
            if r.status>0: 
                l+='| %ICON{led-red}% | '
            else:
                l+='| %ICON{led-green}% | '
            l += r.name+" | "+r.address+" |\n"
            print l
            fi.write(l)
        print "got FAX redirectors from AGIS."
    except:
        print "Unexpected error:", sys.exc_info()[0]
    fi.close()

print '-------------------------------- Writing to GAE -------------------------------------------'

for s in sites:
    data = dict(epName=s.name, epStatus=str(s.status()), epAddress=s.host)
    u = urllib2.urlopen('http://1-dot-waniotest.appspot.com/wanio', urllib.urlencode(data))
    print u.read(), u.code
    
for r in redirectors:
    data = dict(reName=r.name, reStatus=str(r.status), reAddress=r.address)
    u = urllib2.urlopen('http://1-dot-waniotest.appspot.com/wanio', urllib.urlencode(data))
    print u.read(), u.code