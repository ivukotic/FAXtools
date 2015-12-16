#!/usr/bin/env python
import  os, sys, time, datetime
import urllib2, urllib

try: import simplejson as json
except ImportError: import json

headers={ 'Content-Type': 'application/json' }

def MicroTime(t):
    secs=(t-datetime.datetime(1970,1,1)).total_seconds()
    return secs/86400+25569
    
class job:
    
    def prn(self):
        print self.pandaid, self.jobstatus, 
        print self.creationtime, self.starttime,
        print self.duration, self.cpuconsumption,
        print self.wall, self.cpu,
        print self.events, self.size,
        print self.rate
        
        #print time.strftime(" %d/%m %H:%M:%S", self.starttime), time.strftime(" %d/%m %H:%M:%S", self.stoptime), self.wallt(), self.size, self.rate

jobs=[]
succ=fail=0

try:
    req = urllib2.Request("http://bigpanda.cern.ch/jobs/?jeditaskid="+sys.argv[1], None, headers)
    opener = urllib2.build_opener()
    f = opener.open(req,timeout=50)
    res=json.load(f)
    f.close()
    jobsetid=0
    jeditaskid=0
    computingsite=''
    ncleaned=[]
    for j in res:
        if j['jobstatus']=='failed': fail+=1
        if j['jobstatus']=='activated': continue
        if j['jobstatus']=='running': continue
        if j['jobstatus']=='holding': continue
        succ+=1
        # print j['pandaid'],j['jeditaskid'],
        print j['pandaid'], j['jobstatus'],j['currentpriority'], j['computingsite'],j['creationtime'],j['waittime'],j['starttime'],j['duration'],j['cpuconsumptiontime']
        cl=[j['pandaid'], j['jobstatus'],j['currentpriority'],datetime.datetime.strptime(j['creationtime'], '%Y-%m-%dT%H:%M:%S+00:00'),j['waittime'],datetime.datetime.strptime(j['starttime'], '%Y-%m-%dT%H:%M:%S+00:00'),j['duration'],j['cpuconsumptiontime']]
        jo=job()
        jo.pandaid=j['pandaid']
        jo.jobstatus=j['jobstatus']
        jo.currentpriority=j['currentpriority']
        jo.creationtime=datetime.datetime.strptime(j['creationtime'], '%Y-%m-%dT%H:%M:%S+00:00')
        jo.starttime=datetime.datetime.strptime(j['starttime'], '%Y-%m-%dT%H:%M:%S+00:00')
        du=j['duration'].split(':')
        jo.duration=datetime.timedelta(hours=int(du[0]),minutes=int(du[1]),seconds=int(du[2]))
        jo.stoptime=jo.starttime+jo.duration
        jo.cpuconsumption=j['cpuconsumptiontime']
        jo.cpu=0
        jo.wall=0
        jo.size=0
        jo.events=0
        jo.rate=0
        
        jobsetid=j['jobsetid']
        jeditaskid=j['jeditaskid']
        computingsite=j['computingsite']
        found=0
        for i in jobs:
            if i.pandaid==j['pandaid']: found=1
        # for i in ncleaned:
            # if j['pandaid']==i[0]: found=1
        # if not found: ncleaned.append(cl)
        if not found: jobs.append(jo)
            
except:
    print "# Can't load from bigpandamon ", sys.exc_info()[0]

print "jobs:",len(jobs)
jobs.sort(key=lambda x: x.pandaid, reverse=False)
print 'to delete:', jobs[0].prn()
del jobs[0]
print "real jobs :",len(jobs)

for j in jobs: j.prn()

fc=1
print 'pandaid\tjobstatus\tcreationtime\twaittime\tstarttime\tduration\tcpuconsumption\tevents\tzipsize\twall\tcpu'
for s in jobs:
    fn=sys.argv[2]+'/user.ivukotic.'+str(jobsetid).zfill(6)+'._'+str(fc).zfill(6)+'.info.txt'
    fc+=1
    if not os.path.isfile(fn): continue
    f=open(fn, 'r')
    alllines=f.read()
    alllines=alllines.split('\n')
    EVENTS=ZIPSIZE=WALLTIME=CPUTIME=0
    for l in alllines:
        if l.startswith('EVENTS='):
            s.events+=int(l.replace('EVENTS=',''))
        if l.startswith('ZIPSIZE='):
            s.size+=float(l.replace('ZIPSIZE=',''))/1024/1024
        if l.startswith('WALLTIME='):
            s.wall+=float(l.replace('WALLTIME=',''))
        if l.startswith('CPUTIME='):
            s.cpu+=float(l.replace('CPUTIME=',''))

    if s.wall>0: s.rate=(float(s.size))/s.wall
    s.prn()


agreRate={}
runningJobs={}
waitingJobs={}

st=datetime.datetime.max
et=datetime.datetime.min
aw=datetime.timedelta()
jd=datetime.timedelta()
arate=0
acpu=0
awall=0

#adding moments
for j in jobs:
    agreRate[j.starttime]=0
    agreRate[j.starttime+j.duration]=0
    
    runningJobs[j.starttime]=0
    runningJobs[j.starttime+j.duration]=0
    
    waitingJobs[j.creationtime]=0
    waitingJobs[j.starttime]=0
    
    if st>j.creationtime: st=j.creationtime
    if et<(j.starttime+j.duration):et=(j.starttime+j.duration)
    aw+=(j.starttime-j.creationtime)
    arate+=j.rate
    jd+=j.duration
    acpu+=j.cpu
    awall+=j.wall
    
# print 'total job moments:', len(agreRate)
# print 'total wait moments:', len(waitingJobs)




for m in sorted(agreRate.keys()):
    for j in jobs:
        if j.starttime<=m:
            agreRate[m]+=j.rate
            runningJobs[m]+=1
        if j.stoptime<m:
            agreRate[m]-=j.rate
            runningJobs[m]-=1


mr=maxrate=mw=-1

print 'time\tagregate rate\tconcurrent jobs'
for m in sorted(agreRate.keys()):
    if mr<runningJobs[m]: mr=runningJobs[m]
    if maxrate<agreRate[m]: maxrate=agreRate[m]
    print str(MicroTime(m))+'\t'+str(agreRate[m])+'\t'+str(runningJobs[m])

for m in sorted(waitingJobs.keys()):
    for j in jobs:
        if j.creationtime<=m:
            waitingJobs[m]+=1
        if j.starttime<m:
            waitingJobs[m]-=1


print 'time\twaiting jobs'
for m in sorted(waitingJobs.keys()):
    if mw<waitingJobs[m]: mw=waitingJobs[m]
    print str(MicroTime(m))+'\t'+str(waitingJobs[m])


print "source/destination"
print "finished/failed\t"+str(succ-1)+'/'+str(fail)
print "from start to end\t"+str(et-st) 
print "max running jobs\t"+str(mr)
print "average job duration\t"+str(datetime.timedelta(seconds=jd.total_seconds()/len(jobs)))
print "max waiting jobs\t"+str(mw)
print "average waiting time\t"+str(datetime.timedelta(seconds=aw.total_seconds()/len(jobs)))
print "max rate\t"+str(round(maxrate,2))+" MB/s"
print "average rate\t"+str(round(arate/len(jobs),2))+" MB/s"
print "average CPU time\t"+str(round(acpu/len(jobs),2))
print "average WALL time\t"+str(round(awall/len(jobs),2))
print "average CPU eff.\t"+str(round(acpu/awall,2))


# {"ddmerrordiag": "", "inputfiletype": "", "creationtime": "2014-07-30T08:53:07+00:00", "jobstatus": "finished", "vo": "atlas", "waittime": "0:15:17", "destinationse": "", "exeerrorcode": 0, "duration": "0:21:42", "brokerageerrorcode": 0, "cloud": "US", "workinggroup": "", "homepackage": "", "prodsourcelabel": "user", "ddmerrorcode": 0, "produsername": "Sarah Louise Williams", "taskbuffererrordiag": "", "jobdispatchererrorcode": 0, "attemptnr": 1, "superrorcode": 0, "homecloud": null, "taskid": 3, "transexitcode": "0", "jobinfo": "", "currentpriority": 962, "transformation": "runGen-00-00-02", "jobdispatchererrordiag": "", "pandaid": 2230748170, "piloterrorcode": 0, "priorityrange": "900:999", "superrordiag": "", "jobsetid": 108572, "computingelement": "ANALY_BNL_SHORT-condor", "processingtype": "panda-client-0.5.5-jedi-run", "taskbuffererrorcode": 0, "cpuconsumptiontime": 1140, "jobname": "user.williams.TestGrid290714.00206971/", "brokerageerrordiag": "", "atlasrelease": "", "endtime": "2014-07-30T09:30:06+00:00", "computingsite": "ANALY_BNL_SHORT", "exeerrordiag": "", "jobsetrange": "108500:108599", "errorinfo": "", "inputfileproject": "user", "jeditaskid": 4002606, "specialhandling": "", "modificationtime": "2014-07-30T09:50:15+00:00", "starttime": "2014-07-30T09:08:24+00:00", "piloterrordiag": ""}