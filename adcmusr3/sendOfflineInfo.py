#!/usr/bin/env python
import os, sys, time, datetime
import urllib, urllib2

try: import simplejson as json
except ImportError: import json

from agisconf import agis

# getting downed sites
# unneded statuslist = agis.get_site_status(activity='DDMFT')

downtimes_ongoing = agis.list_downtimes(ongoing_time=datetime.datetime.utcnow())
downed=set()
for i in downtimes_ongoing:
     for en in range(len(downtimes_ongoing[i])):
          afs=downtimes_ongoing[i][en].affected_services
          if ('SRM' in afs or 'SRMv2' in afs):
               print "Affected site:", i, afs
               downed.add(i)

json_data = json.dumps(list(downed))
print json_data

try:
    req = urllib2.Request("http://waniotest.appspot.com/OfflineInfo",json_data,{ 'Content-Type': 'application/json' })
    opener = urllib2.build_opener()
    f = opener.open(req,timeout=50)
    res=f.read()
    print res
    f.close()
except:
    print "# Can't upload to GAE", sys.exc_info()[0]
    
print 'done'
