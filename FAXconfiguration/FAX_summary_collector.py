#!/usr/bin/env python
import os, sys, subprocess, threading, time, datetime, atexit
import logging,  pickle
import  urllib, urllib2, socket

import xml.dom.minidom 

try: import simplejson as json
except ImportError: import json

logging.basicConfig()

def clear_files():
    try:
        os.unlink('getSummaryInfo.sh')      
    except Exception,e:
        print "could not remove the file:"+str(e)

class redirector:
    def __init__(self, name, address):
        self.name=name
        self.address=address
        self.upstream=False
        self.downstream=False
        self.status=0 # b001 - can not check, b010-no downstream, b1x0-no downstream 
        self.ips=[]
    def prnt(self):
        print 'redirector: ', self.name, '\taddress: ', self.address, '\t upstream:', self.upstream, '\t downstream:', self.downstream, '\t status:', self.status
        for ip in self.ips: ip.prnt()

class host:
    def __init__(self, ip):
        self.ip=ip
        self.tos=0
        self.loadPrevious()
    def loadPrevious(self):
        fn='previous_'+self.ip+'.state'
        if not os.path.isfile(fn): 
            self.old=None
            return 
        with open(fn, 'r') as f:
            self.old=pickle.load(f)
    def writeNew(self):
        fn='previous_'+self.ip+'.state'
        with open(fn, 'w') as f:
            pickle.dump(self, f)
    def prnt(self):
        print 'ip:',self.ip, 'tos:',self.tos

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
    

workingDir='./' #'/afs/cern.ch/user/i/ivukotic/FAXtools/FAXconfiguration/'
redirectors=[]
timeouts=5
sleeps=10

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

        
def dnsalias_to_nodes(redirector):
    ho = redirector.address.split(':')[0]
    try: 
        data=socket.getaddrinfo(ho,1094,0, 0, socket.SOL_TCP )
    except:
        print "Unexpected error:", sys.exc_info()[0] 
        return []
    for addr in data:
        (family, socktype, proto, canonname, sockaddr) = addr
        (hostname, aliaslist, ipaddrlist) = socket.gethostbyaddr(sockaddr[0])    
        redirector.ips.append(host(hostname))

for r in redirectors:
    dnsalias_to_nodes(r)
    r.prnt()
    

print 'Geting info'

        
atexit.register(clear_files)
logpostfix='.log'
with open('getSummaryInfo.sh', 'w') as f: # ask redirectors for their data
    for r in redirectors:
        for host in r.ips:
            logfile='summaryInfo_'+r.name+'_'+host.ip+logpostfix
            comm = 'xrdfs '+ host.ip + ' query stats a > ' + logfile + ' & \n'
            f.write('echo "command executed:\n ' + comm + '" >> ' + logfile + '\n')
            f.write('echo "========================================================================" >> ' + logfile + '\n')
            f.write(comm)            
    f.close()

print 'executing all of the xrdcps in parallel. 5 min timeout.'
com = Command("source " + workingDir + "getSummaryInfo.sh")    
com.run(timeouts)
time.sleep(sleeps)    

print 'checking log files'

for r in redirectors:  # this is file to be asked for
    for host in r.ips:
        logfile='summaryInfo_'+r.name+'_'+host.ip+logpostfix
        with open(logfile, 'r') as f:
            doc=f.readline()
            if doc=='': continue
            print doc
            try:
                print 'start parsig'
                dom = xml.dom.minidom.parseString(doc)
                root_node = dom.documentElement
                if root_node.tagName == 'statistics':
                    n_tos = root_node.getAttributeNode('tos')
                    host.tos = n_tos.nodeValue
                    print 'tos >>>> ',n_tos.nodeValue
            except Exception,e:
                print "ERROR: cannot parse doc:"+str(e)

for r in redirectors: 
    for host in r.ips:
        host.writeNew()
    r.prnt()

