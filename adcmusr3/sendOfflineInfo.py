#!/usr/bin/env python
import sys
import time, datetime
import json
import socket
import urllib, urllib2

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


print 'done'
