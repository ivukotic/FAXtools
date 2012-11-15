#!/usr/bin/env python
import subprocess, threading, os, sys, cx_Oracle,time

import smtplib
from email.mime.text import MIMEText

timeouts=300
sleeps=250

line=''

with open('/afs/cern.ch/user/i/ivukotic/private/OracleAccess.txt', 'r') as f: 
    lines=f.readlines()
    for line in lines:
        if 'ATLAS_WANHCTEST' in line:
            break
    f.close()

sites=[]; # each site contains [name, host, redirector, siteid]

class site:    
    name=''
    host=''
    redirector=0
    siteid=0
    direct=0
    redirects=0
    responsable=''
    responsableName=''
    comm1=''
     
    def __init__(self, na, ho, re, si, resp, respName):
        self.name=na
        self.host=ho
        self.redirector=re
        self.siteid=si
        self.responsable=resp
        self.responsableName=respName
    
    def prnt(self, what):
        if (what>=0 and self.redirector!=what): return
        print 'id:', self.siteid, '\tredirector:', self.redirector, '\tname:', self.name, '\thost:', self.host, '\tresponds:', self.direct, '\t redirects:', self.redirects
    

 
    


        

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
    


def getSiteID(host):
    for s in sites:
        if s.host==host:
            return s.siteid
    print 'redirector -',host,'- does not exist in the db.'
    return 0 


def getHost(siteid):
    for s in sites:
        if s.siteid==siteid:
            return s.host
    print 'no site with siteid=',siteid,'.'
    return 0


print 'Geting site list ...'

try:
    connection = cx_Oracle.Connection(line)
    cursor = cx_Oracle.Cursor(connection)
    print 'Connection established.'

    cursor.execute("SELECT  name, host, redirector, siteid, responsable, responsableName FROM faxsites WHERE active=1")
    res = cursor.fetchall()
    cursor.close()
    for r in res:
        s=site(r[0],r[1],r[2],r[3],r[4],r[5])
        sites.append(s)
    print 'got', len(sites), 'sites.'
    print
except cx_Oracle.DatabaseError, exc:
    error, = exc.args
    print "FAX_configuration_tests.py - problem in establishing connection to db"
    print "FAX_configuration_tests.py Oracle-Error-Code:", error.code
    print "FAX_configuration_tests.py Oracle-Error-Message:", error.message

for s in sites: s.prnt(-1) # print all
print 'creating scripts to execute'
    

print "================================= CHECK I =================================================="
    
with open('toExecute.sh', 'w') as f: # first check that site itself gives it's own file
    for s in sites:
        if s.redirector>0: continue
        logfile=s.name+'_to_'+s.name+'.log'
        lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.'+s.name+'-1M'
        s.comm1='xrdcp -f -np -d 1 root://'+s.host+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
        f.write(s.comm1)
    f.close()

print 'executing all of the xrdcps in parallel. 5 min timeout.'
com = Command("source toExecute.sh")    
com.run(timeouts)
time.sleep(sleeps)



print 'checking log files'
alllinks=set()

# checking which sites gave their own file directly
for s in sites:  # this is file to be asked for
    if s.redirector>0: continue # only genuine sites
    logfile=s.name+'_to_'+s.name+'.log'
    with open(logfile, 'r') as f:
        lines=f.readlines()
        succ=False
        for l in lines:
            # print l
            if l.startswith(" BytesSubmitted"):
                succ=True
                break
        if succ==True:
            print logfile, "works"
            s.direct=1    
        else:
            print logfile, "problem"
            # send mail
            # pass
            try:
                 smt = smtplib.SMTP()
                 smt.connect()   
                 
                 body= '\nDear '+s.responsableName+',\n\n\tA cron job analysing FAX infrastructure readiness detected that it could not receive '
                 body+='a file that is unique to your site, by directly demanding it from '+s.host+'. Command executed was:\n '
                 body+=s.comm1
                 body+='\nLog file is available through a web page:\n http://ivukotic.web.cern.ch/ivukotic/FAX/index.asp.\n\tPlease be so kind as to investigate and correct the problem.\n'
                 body+='\tIn case there was a change of then FAX door host or your are not a responsable person, please send mail to ivukotic@cern.ch so test configuration can be updated.\n\n'
                 body+='Yours trully,\n FAX checking deamon.\n'
                 msg = MIMEText(body) 
                 msg['Subject'] = 'FAX service problem at '+s.name+' observed.'
                 msg['From'] = 'fax.door.checker@cern.ch'
                 msg['To'] = s.responsable
                 
                 smt.sendmail('ivukotic@cern.ch', s.responsable, msg.as_string())
                     
                 smt.quit()
             
            except smtplib.SMTPException:
                print "Error: unable to send mail."
                    

                
            
for s in sites: s.prnt(0)  #print only real sites


print "================================= CHECK II ================================================="

with open('checkRedirection.sh', 'w') as f: # ask good sites for unexisting file
    for s in sites:
        if s.redirector>0 or s.direct==0: continue
        logfile='redirectFrom_'+s.name+'.log'
        lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.unexisting-1M'
        comm='xrdcp -f -np -d 1 root://'+s.host+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
        f.write(comm)            
    f.close()
    
print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
com = Command("source checkRedirection.sh")    
com.run(timeouts)
time.sleep(sleeps)

for s in sites:
    if s.redirector>0 or s.direct==0: continue
    logfile='redirectFrom_'+s.name+'.log'
    with open(logfile, 'r') as f:
        print logfile
        lines=f.readlines()        
        reds=[]
        for l in lines:
            if l.count("Received redirection")>0:
                red=l[l.find("[")+1 : l.find("]")]
                reds.append(red.split(':')[0])
        links=[]
        print 'redirections:',reds
        if len(reds)==0:
            s.redirects=0
            print 'redirection does not work'
        else:    
            s.redirects=1
            links.append( [s.host, reds[0] ] )
            alllinks.add( s.siteid * 10000 + getSiteID(reds[0]) )
            lr=len(reds)
            for c in range(lr-1):
                links.append([reds[c],reds[c+1]])
                alllinks.add( getSiteID(reds[c]) * 10000 + getSiteID(reds[c+1]) )
            print 'links: ', links



try: # updateing values in the db.
    connection = cx_Oracle.Connection(line)
    cursor = cx_Oracle.Cursor(connection)
    print 'Connection established.'
    for s in sites:
        com='UPDATE faxsites SET direct='+str(s.direct)+', redirects='+ str(s.redirects)+' WHERE siteid='+str(s.siteid) 
        cursor.execute(com)
        connection.commit()
        print s.name,'updated.'
    cursor.close()
    print
except cx_Oracle.DatabaseError, exc:
    error, = exc.args
    print "FAX_configuration_tests.py - problem in establishing connection to db"
    print "FAX_configuration_tests.py Oracle-Error-Code:", error.code
    print "FAX_configuration_tests.py Oracle-Error-Message:", error.message

print "================================= CHECK III ================================================"

with open('checkUpDown.sh', 'w') as f: # ask global redirectors for files belonging to good sites
    for red in [16,17]:        
        for s in sites:
            if s.redirector>0 or s.direct==0: continue
            logfile='checkUpDown_'+getHost(red)+'_to_'+s.name+'.log'
            lookingFor = 'user.HironoriIto.xrootd.'+s.name+'/user.HironoriIto.xrootd.'+s.name+'-1M'
            comm='xrdcp -f -np -d 1 root://'+getHost(red)+'//atlas/dq2/user/HironoriIto/'+lookingFor+' /dev/null >& '+logfile+' & \n'
            f.write(comm)            
    f.close()

print 'executing all of the redirection xrdcps in parallel. 5 min timeout.'
com = Command("source checkUpDown.sh")    
com.run(timeouts)
time.sleep(sleeps)



for d in [16,17]:        
    for s in sites:
        if s.redirector>0 or s.direct==0: continue
        logfile='checkUpDown_'+getHost(d)+'_to_'+s.name+'.log'
        with open(logfile, 'r') as f:
            print 'Checking file: ', logfile
            lines=f.readlines()
            succ=False
            reds=[]
            for l in lines:
                if l.startswith(" BytesSubmitted"):
                    succ=True
            if succ==False: 
                print 'Did not work.' 
                continue                
            print 'OK'
            reds=[]
            for l in lines:
                if l.count("Received redirection")>0:
                    red=l[l.find("[")+1 : l.find("]")]
                    reds.append(red.split(':')[0])
            links=[]
            print 'redirections:',reds
            if len(reds)==0:
                s.redirects=0
                print 'redirection does not work'
            else:    
                s.redirects=1
                links.append( [getHost(d), reds[0] ] )
                print d, reds[0], d * 10000 + getSiteID(reds[0])
                alllinks.add( d * 10000 + getSiteID(reds[0]) )
                lr=len(reds)
                for c in range(lr-1):
                    links.append([reds[c],reds[c+1]])
                    if getSiteID(reds[c])==0 or getSiteID(reds[c+1])==0: continue
                    
                    print getSiteID(reds[c]), getSiteID(reds[c+1]), getSiteID(reds[c]) * 10000 + getSiteID(reds[c+1])
                    alllinks.add( getSiteID(reds[c]) * 10000 + getSiteID(reds[c+1]) )
                print 'links: ', links
                
for i in alllinks:
    s=int(round(i/10000))
    d=int(i-round(i/10000)*10000)
    if s==d:
        print 'source and destination the same. skip'
        continue
    if getHost(s)==0 or getHost(d)==0: continue
    print 'uploading -  s:',s,'\td:',d,'\tfile from:',getHost(s),"\t was asked from:",getHost(d)
                                          
try:
    cursor1 = cx_Oracle.Cursor(connection)
    print 'upload of links prepared.'
    for i in alllinks:
        s=int(round(i/10000))
        d=int(i-round(i/10000)*10000)
        if getHost(s)==0 or getHost(d)==0: continue
        print 'uploading: ',s,d,'file from:',getHost(s),"\t was asked from:",getHost(d)
        cursor1.execute( 'INSERT INTO faxlink  (source, destination) VALUES (' +str(s) + ',' + str(d) + ')' )
    cursor1.close()
    connection.commit()
    print 'done'
except cx_Oracle.DatabaseError, exc:
    error, = exc.args
    print "FAX_configuration_tests.py - problem in establishing connection to db"
    print "FAX_configuration_tests.py Oracle-Error-Code:", error.code
    print "FAX_configuration_tests.py Oracle-Error-Message:", error.message
        
