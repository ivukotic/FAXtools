#!/usr/bin/env python

import subprocess, threading, os, sys,time
import datetime, random
import urllib2

try:
	import simplejson as json
except ImportError:
	import json

        
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
    
    
def createDataset(name):
    print "Creating a new dataset..."
    com = Command('./createTestFiles.sh '+name)
    print com.run(600)
    
def subscribeDataset(name,to):
    print "Subscribing the dataset to:", to
    com = Command('dq2-register-subscription user.ivukotic.xrootd.' + name + ' ' + to)
    print com.run(200)

def deleteDataset(name, at):
    print "Deleting the replica at:", at
    com = Command('dq2-delete-replicas user.ivukotic.xrootd.'+name+' '+ at )
    print com.run(200)
    

print 'Geting site list from AGIS...'


sites={}


try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/site/query/list/?json&vo_name=atlas&state=ACTIVE", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        if  s["tier_level"]>2 or len(s["ddmendpoints"])==0 : continue
        print  s["name"],s["rc_site"],  s["tier_level"], s["ddmendpoints"]
        if s["name"]=='ru-Moscow-SINP-LCG2': continue
        sites[s["name"]]=[s["rc_site"],  s["tier_level"], s["ddmendpoints"]]
except:
    print "Unexpected error:", sys.exc_info()[0]


#com = Command('dq2-ls -r user.ivukotic.xrootd.* > datasets.txt')     
#print com.run(600)

exi={}
with open("datasets.txt", 'r') as f:
    lines=f.readlines()
    for l in lines:
        l=l.strip()
        if l.count("INCOMPLETE"): continue
        if l.startswith('user.ivukotic.xrootd.'):
            cs=l.replace('user.ivukotic.xrootd.','').replace(':','').split('.')
            cs=cs[0]
        if l.startswith('COMPLETE:'):
            ddms=l.replace('COMPLETE: ','')
            exi[cs]=ddms.split(',')

print exi

toFix={}
for name in sites:
    found=0
    for ename in exi:
        if name.lower()!=ename: continue
        found+=1
        dfound=0
        for ddm in sites[name][2].keys():
            if ddm in exi[ename]:
                dfound+=1
                
    print "Site:",name,    
    if found==0:
        print "has no test dataset."
        toFix[name]=0
    else:
        if dfound==0:
            print "has no test dataset delivered.",
            toFix[name]=1
            if len(exi[name.lower()])>0:
                print "dataset exists at other place.",exi[name.lower()]
                toFix[name]=2
            else:
                print
        else:
            if len(exi[name.lower()])>1:
                print "dataset exists at additional place.",exi[name.lower()]
                toFix[name]=3
            else:
                print 'is OK.'
print "================================="
#print toFix

for name in toFix:
    print "----------------------\nFixing site:", name, 
    n=name.lower()
    if toFix[name]==0:
        createDataset(n)
        subscribeDataset(n, n.upper()+'_DATADISK')
    if toFix[name]==1:
        subscribeDataset(n, n.upper()+'_DATADISK')
    if toFix[name]==2:
        print 'will wait for copy to arrive.'
    if toFix[name]==3:
        print "Deleting extraneous copies..."
        for dd in exi[n]:
            print dd
            if dd.count(n.upper())==0: 
                deleteDataset(n, dd)
