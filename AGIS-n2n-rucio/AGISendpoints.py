#!/usr/bin/env python

import os, sys

# sites=[]; # each site contains [name, host, redirector]

# class site:    
#     name=''
#     host=''
#     redirector=''
#     direct=0
#     upstream=0
#     downstream=0
#     comm1=''
#      
#     def __init__(self, na, ho, re):
#         self.name=na
#         self.host=ho
#         self.redirector=re
#     
#     def prnt(self, what):
#         if (what>=0 and self.redirector!=what): return
#         print '\tredirector:', self.redirector, '\tname:', self.name, '\thost:', self.host, '\tresponds:', self.direct, '\t upstream:', self.upstream, '\t downstream:', self.downstream
#     

print 'Geting ddmpoint list from AGIS...' 

import urllib2,simplejson

try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=simplejson.load(f)
    for s in res:
        print  s["name"], s["endpoint"]
        prot=s["protocols"]
        for p in prot:
            print " --> ", p
            dirs=prot[p]
            for d in dirs:
                if "r" in d:
                    print " -----> ", d
        # , s["redirector"]["endpoint"]
        # si=site(s["rc_site"].lower(), s["endpoint"], s["redirector"]["endpoint"])
        # sites.append(si)
except:
    print "Unexpected error:", sys.exc_info()[0]    




        

# class Command(object):
#     
#     def __init__(self, cmd):
#         self.cmd = cmd
#         self.process = None
#     
#     def run(self, timeout):
#         def target():
#             print 'command started: ', self.cmd
#             self.process = subprocess.Popen(self.cmd, shell=True)
#             self.process.communicate()
#         
#         thread = threading.Thread(target=target)
#         thread.start()
#         
#         thread.join(timeout)
#         if thread.is_alive():
#             print 'Terminating process'
#             self.process.terminate()
#             thread.join()
#         return self.process.returncode
#     
# 
# 
# for s in sites: s.prnt(-1) # print all
# print 'creating scripts to execute'
#     
# print "================================= CHECK I =================================================="
#     
# with open('checkDirect.sh', 'w') as f: # first check that site itself gives it's own file
#     for s in sites:
#         logfile=s.name+'_to_'+s.name+'.log'
#         lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.'+s.name+'-1M'
#         s.comm1='xrdcp -f -np -d 1 '+s.host+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
#         f.write(s.comm1)
#     f.close()
# 
# #sys.exit(0)
# print 'executing all of the xrdcps in parallel. 5 min timeout.'
# com = Command("source checkDirect.sh")    
# com.run(timeouts)
# time.sleep(sleeps)
# 
# 
# print 'checking log files'
# 
# # checking which sites gave their own file directly
# for s in sites:  # this is file to be asked for
#     logfile=s.name+'_to_'+s.name+'.log'
#     with open(logfile, 'r') as f:
#         lines=f.readlines()
#         succ=False
#         for l in lines:
#             # print l
#             if l.startswith(" BytesSubmitted"):
#                 succ=True
#                 break
#         if succ==True:
#             print logfile, "works"
#             s.direct=1
#         else:
#             print logfile, "problem"
#             
# for s in sites: s.prnt(0)  #print only real sites
# 
# #sys.exit(0)
# 
# print "================================= CHECK II ================================================="
# 
# with open('checkUpstream.sh', 'w') as f: # ask good sites for unexisting file
#     for s in sites:
#         if s.direct==0: continue
#         logfile='upstreamFrom_'+s.name+'.log'
#         lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.unexisting-1M'
#         comm='xrdcp -f -np -d 1 '+s.host+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
#         f.write(comm)            
#     f.close()
#     
# print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
# com = Command("source checkUpstream.sh")    
# com.run(timeouts)
# time.sleep(sleeps)
# 
# 
# for s in sites:
#     if s.direct==0: continue
#     logfile='upstreamFrom_'+s.name+'.log'
#     with open(logfile, 'r') as f:
#         print logfile
#         lines=f.readlines()        
#         reds=[]
#         for l in lines:
#             if l.count("Received redirection")>0:
#                 red=l[l.find("[")+1 : l.find("]")]
#                 reds.append(red.split(':')[0])
#         print 'redirections:',reds
#         if len(reds)==0:
#             s.upstream=0
#             print 'redirection does not work'
#         else:    
#             s.upstream=1
#             print 'redirection works'
# 
# #sys.exit(0)
# print "================================= CHECK III ================================================"
# 
# with open('checkDownstream.sh', 'w') as f: # ask global redirectors for files belonging to good sites
#     for s in sites:
#         if s.direct==0: continue
#         logfile='checkDownstream_'+s.redirector+'_to_'+s.name+'.log'
#         lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.'+s.name+'-1M'
#         comm='xrdcp -f -np -d 1 root://'+s.redirector+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
#         f.write(comm)            
#     f.close()
# 
# print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
# com = Command("source checkDownstream.sh")    
# com.run(timeouts)
# time.sleep(sleeps)
# 
# for s in sites:
#     if s.direct==0: continue
#     logfile='checkDownstream_'+s.redirector+'_to_'+s.name+'.log'
#     with open(logfile, 'r') as f:
#         print 'Checking file: ', logfile
#         lines=f.readlines()
#         succ=False
#         reds=[]
#         for l in lines:
#             if l.startswith(" BytesSubmitted"):
#                 succ=True
#                 s.downstream=1
#         if succ==False: 
#             print 'Did not work.'
#             s.downstream=0 
#             continue                
#         print 'OK'
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
