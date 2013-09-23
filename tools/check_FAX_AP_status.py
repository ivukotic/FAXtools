#!/usr/bin/env python
import os, sys, time, getopt
from  datetime import datetime
from datetime import timedelta
try: 
	import simplejson as json
except ImportError: 
	import json

import urllib2

curtime=datetime.now()


class site:
    name=''
    cloud=''
    direct=0
    upstream=0
    downstream=0
    
    def __init__(self,na,cl):
        self.name=na
        self.cloud=cl
    def prn(self):
        print self.name
        print  "direct: ",self.direct
        print  "upstream: ",self.upstream
        print  "downstream: ",self.downstream

    
def usage():
    print "usage: check_FAX_AP_status.py -s/--site [-v/--verbose] [-h/--help] SITE_NAME \nreturned code consist of 3 numbers: direct access, upstream redirection, downstream redirection. \n3 - not working, 5 - working, 7 - offline"
    

def main(argv=None):
    
    
    if argv is None:
        argv = sys.argv
    
    verbose=False
    siteToCheck=''
        
    try:
        opts, args = getopt.getopt(argv[1:], "hvs:", ["help","verbose","site="])
        for o, a in opts:
                if o == "-v":
                    verbose = True
                elif o in ("-h", "--help"):
                    usage()
                    sys.exit()
                elif o in ("-s", "--site"):
                    siteToCheck = a
                    
    except getopt.error, msg:
         usage()
         print str(msg)
         sys.exit(2)
                
    #direct
    url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10083"
    if verbose:
        print url
    try:
    	response=urllib2.Request(url,None)
    	opener = urllib2.build_opener()
    	f = opener.open(response)
    	data = json.load(f)
    	data=data["csvdata"]
    except:
        print "Unexpected error:", sys.exc_info()[0]

    Sites=dict()
    for si in data:
    	n=si['VOName']
    	if n not in Sites:
    		s=site(n,si['Cloud'])
    		Sites[n]=s
    	et=datetime.strptime(si["EndTime"],'%Y-%m-%dT%H:%M:%S')
    	if et>curtime: # current state
    		Sites[n].direct=si['COLOR']

    #upstream
    url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10084"
    if verbose:
        print url
    try:
            response=urllib2.Request(url,None)
            opener = urllib2.build_opener()
            f = opener.open(response)
            data = json.load(f)
            data=data["csvdata"]
    except:
        print "Unexpected error:", sys.exc_info()[0]

    for si in data:
            n=si['VOName']
            if n not in Sites:
                    s=site(n,si['Cloud'])
                    Sites[n]=s
            et=datetime.strptime(si["EndTime"],'%Y-%m-%dT%H:%M:%S')
            if et>curtime: # current state
                    Sites[n].upstream=si['COLOR']


    #downstream
    url="http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=1&dateFrom=&dateTo=&sites=all&clouds=all&batch=1&columnid=10085"
    if verbose:
        print url
    try:
            response=urllib2.Request(url,None)
            opener = urllib2.build_opener()
            f = opener.open(response)
            data = json.load(f)
            data=data["csvdata"]
    except:
        print "Unexpected error:", sys.exc_info()[0]

    for si in data:
            n=si['VOName']
            if n not in Sites:
                    s=site(n,si['Cloud'])
                    Sites[n]=s
            st=datetime.strptime(si["Time"],'%Y-%m-%dT%H:%M:%S')
            et=datetime.strptime(si["EndTime"],'%Y-%m-%dT%H:%M:%S')
            if et>curtime: # current state
                    Sites[n].downstream=si['COLOR']

     
    for s in Sites:   	
        if verbose or s.startswith(siteToCheck.upper()):
            Sites[s].prn()
    
if __name__ == "__main__":
    sys.exit(main())
    