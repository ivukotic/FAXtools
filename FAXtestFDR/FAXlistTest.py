#!/usr/bin/env python

import subprocess, threading, os, sys,time
import stomp, logging, datetime, ConfigParser, random

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
        

        
class Command(object):
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
    
    def run(self, timeout):
        def target():
            print 'command started: ', self.cmd
            self.process = subprocess.Popen(self.cmd, shell=True)
            return self.process.communicate()[0]
        
        thread = threading.Thread(target=target)
        thread.start()
        
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode
    
    
        

sites=[]; # each site contains [name, host, redirector]

class site:
    name=''
    fullname=''
    host=''
    redirector=''
    successes=0
    fails=0
    comm1=''


    def __init__(self, fn, na, ho, re):
        if na=='grif':
            na=fn
        self.fullname=fn
        self.name=na
        self.host=ho
        self.redirector=re


    def prnt(self):
        print  self.name, '\tsuccesses:', self.successes, '\t fails:', self.fails



print 'Geting site list from AGIS...'

import urllib2,simplejson

try:
    req = urllib2.Request("http://atlas-agis-api-0.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=simplejson.load(f)
    for s in res:
        #print  s["name"],s["rc_site"], s["endpoint"], s["redirector"]["endpoint"]
        si=site(s["name"].lower(),s["rc_site"].lower(), s["endpoint"], s["redirector"]["endpoint"])
        si.prnt()
        sites.append(si)
except:
    print "Unexpected error:", sys.exc_info()[0]


# read file list file
files=[]
with open("inputFiles.txt", 'r') as f:
    lines=f.readlines()
    for l in lines:
        files.append(l.rstrip())
        # print l
        
for s in sites:
    if s.name!='mwt2': continue
    sname=s.name.upper()
    for f in files:
        nfile=f.replace("root://fax.mwt2.org",s.host).replace("MWT2",sname)
        print nfile
        c='root -q -b "list.C(\\"'+nfile+'\\")" >> '+sname+'.log &'
        com = Command(c)    
        if (com.run(60)!=0):
            s.fails+=1
        else:
            s.successes+=1
    print sname, "\tsuccesses:",s.successes,"\t\tfails:" ,s.fails,"\t\tsuccess rate: ",s.successes*100./(s.successes+s.fails)," %"
        

#                 
# print '--------------------------------- Uploading results ---------------------------------'
# ts=datetime.datetime.now()
# ts=ts.replace(microsecond=0)
# for s in sites:
#     sta='0'
#     if s.direct==1: sta='1'
#     if s.upstream==1 and s.downstream==0: sta='2'
#     if s.upstream==0 and  s.downstream==1: sta='3'
#     if s.upstream==1 and  s.downstream==1: sta='4' 
#     send ('siteName: '+ s.name + '\nmetricName: FAXprobe1\nmetricStatus: '+sta+'\ntimestamp: '+ts.isoformat(' ')+'\n')      
