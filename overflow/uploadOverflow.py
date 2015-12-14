#!/usr/bin/env python
import  os, sys, time, datetime
import urllib2, urllib

try: import simplejson as json
except ImportError: import json

print '-----------------------STARTING--------------'
print datetime.datetime.now()

headers={ 'Content-Type': 'application/json' }

try:
    req = urllib2.Request("http://bigpanda.cern.ch/jobs/?transfertype=fax&limit=100000&hours=1&json", None, headers)
    opener = urllib2.build_opener()
    f = opener.open(req,timeout=600)
    res=json.load(f)
    f.close()
    cleaned=[]
    for j in res:
        if j['jobstatus']=='cancelled': continue
        if j['jobstatus']=='activated': continue
        if j['jobstatus']=='running': continue
        if j['jobstatus']=='holding': continue
        if j['jobstatus']=='defined': continue
        if j['jobstatus']=='merging': continue
        print j['pandaid'],j['jeditaskid'], j['jobstatus'],j['currentpriority'], j['computingsite'],j['produsername'],j['creationtime'],j['waittime'],j['duration'],j['cpuconsumptiontime']
        jo=[j['pandaid'],j['jeditaskid'], j['jobstatus'],j['currentpriority'], j['computingsite'],j['produsername'],j['creationtime'],j['waittime'],j['duration'],j['cpuconsumptiontime']]
        cleaned.append(jo)
    json_data = json.dumps(cleaned)
except URLError as e:
    print "# Can't load from bigpandamon ", e.reason
    sys.exit(1)
except:
    print "# Can't load from bigpandamon ", sys.exc_info()[0]
    sys.exit(1)

print json_data

try:
    req = urllib2.Request("http://waniotest.appspot.com/CopyOverflow",json_data,{ 'Content-Type': 'application/json' })
    opener = urllib2.build_opener()
    f = opener.open(req,timeout=50)
    res=f.read()
    print res
    f.close()
except:
    print "# Can't upload to GAE", sys.exc_info()[0]



# {"ddmerrordiag": "", "inputfiletype": "", "creationtime": "2014-07-30T08:53:07+00:00", "jobstatus": "finished", "vo": "atlas", "waittime": "0:15:17", "destinationse": "", "exeerrorcode": 0, "duration": "0:21:42", "brokerageerrorcode": 0, "cloud": "US", "workinggroup": "", "homepackage": "", "prodsourcelabel": "user", "ddmerrorcode": 0, "produsername": "Sarah Louise Williams", "taskbuffererrordiag": "", "jobdispatchererrorcode": 0, "attemptnr": 1, "superrorcode": 0, "homecloud": null, "taskid": 3, "transexitcode": "0", "jobinfo": "", "currentpriority": 962, "transformation": "runGen-00-00-02", "jobdispatchererrordiag": "", "pandaid": 2230748170, "piloterrorcode": 0, "priorityrange": "900:999", "superrordiag": "", "jobsetid": 108572, "computingelement": "ANALY_BNL_SHORT-condor", "processingtype": "panda-client-0.5.5-jedi-run", "taskbuffererrorcode": 0, "cpuconsumptiontime": 1140, "jobname": "user.williams.TestGrid290714.00206971/", "brokerageerrordiag": "", "atlasrelease": "", "endtime": "2014-07-30T09:30:06+00:00", "computingsite": "ANALY_BNL_SHORT", "exeerrordiag": "", "jobsetrange": "108500:108599", "errorinfo": "", "inputfileproject": "user", "jeditaskid": 4002606, "specialhandling": "", "modificationtime": "2014-07-30T09:50:15+00:00", "starttime": "2014-07-30T09:08:24+00:00", "piloterrordiag": ""}
