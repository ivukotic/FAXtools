import urllib2, sys, json

class site:
    def __init__(self):
        self.size=0
        self.files=0
        self.fax=0
        self.tier=4
    def prnt(self):
        return '\tfiles:'+ str(self.files)+ '\tsize:'+str(self.size)+ '\tfax:'+ str(self.fax) +'\ttier:'+ str(self.tier)

sites={}

# get bytes data from ddm
try:
    req = urllib2.Request("http://dashb-atlas-job-prototype.cern.ch/dashboard/request.py/snapshot_viewjson?sites=All%20T210&sitesCat=All%20Clouds&spacetokens=All%20Endpoints&sitesSort=6&sitesCatSort=1&start=null&end=null&timeRange=last24&granularity=Daily&gen_spacetoken=0&gen_project=0&gen_datatype=0&gen_streamname=0&sortBy=0&series=All&prettyprint&type=physbyte", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)["jobs"]
    for s in res:
        #print s["S_SITE"], s["SUM"]
        ns = site()
        ns.size=s["SUM"]
        sites[s["S_SITE"]]=ns
except:
    print "Unexpected error:", sys.exc_info()[0]


# get files data from ddm
try:
    req = urllib2.Request("http://dashb-atlas-job-prototype.cern.ch/dashboard/request.py/snapshot_viewjson?sites=All%20T210&sitesCat=All%20Clouds&spacetokens=All%20Endpoints&sitesSort=6&sitesCatSort=1&start=null&end=null&timeRange=last24&granularity=Daily&gen_spacetoken=0&gen_project=0&gen_datatype=0&gen_streamname=0&sortBy=0&series=All&prettyprint&type=physfile", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)["jobs"]
    for s in res:
        #print s["S_SITE"], s["SUM"]
        if s["S_SITE"] not in sites:
            print "problem. adding site"
            sites["S_SITE"]=site()
        sites[s["S_SITE"]].files=s["SUM"]
except:
    print "Unexpected error:", sys.exc_info()[0]


    
    
# getting fax enabled sites

try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        #print s["rc_site"]
        sname=s["rc_site"].upper()
        if sname=="GRIF": 
            sname=s["name"].upper()
        if sname not in sites:
            print "FAX site could not be found: ",  sname
        else:
            sites[sname].fax=1
except:
    print "Unexpected error:", sys.exc_info()[0]

# getting tier levels

try:
    req = urllib2.Request("http://atlas-agis-api.cern.ch/request/site/query/list/?json&vo_name=atlas", None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    res=json.load(f)
    for s in res:
        #print s["rc_site"]
        sname=s["rc_site"].upper()
        if sname=="GRIF": 
            sname=s["name"].upper()
        if sname not in sites:
            print "site could not be found: ",  sname
        else:
            sites[sname].tier=s["rc_tier_level"]
except:
    print "Unexpected error:", sys.exc_info()[0]
    
    

for s in sites:
    print s, sites[s].prnt()    

totSites=0
faxSites=0
totSize=0
faxSize=0
totFiles=0
faxFiles=0    
for si in sites:
    s=sites[si]
    if s.tier==3 and s.fax==0: 
        print "skipping tier3:", si
        continue
    if s.tier==4: 
        print "skipping unknown tier:", si
        continue
    totSites+=1
    totSize+=s.size
    totFiles+=s.files
    if s.fax==1:
        faxSites+=1
        faxSize+=s.size
        faxFiles+=s.files
    
print 'totSites' , totSites
print 'faxSites' , faxSites, float(faxSites)/totSites*100,"%"
print 'totSize ' , totSize
print 'faxSize ' , faxSize, float(faxSize)/totSize*100,"%"
print 'totFiles' , totFiles
print 'faxFiles' , faxFiles, float(faxFiles)/totFiles*100 ,"%"

f = open('coverage.log', 'w')
f.write('%TABLE{name="Table1"}%')
f.write('|   | Sites | Files | Size [TB] |')
f.write('| FAX | '+str(faxSites)+' | '+str(faxFiles)+' | '+str(faxSize)+' |')
f.write('| Total | '+str(totSites)+' | '+str(totFiles)+' | '+str(totSize)+' |')
f.write('| Coverage | '+str(round(faxSites/totSites*100))+' | '+str(round(faxFiles/totFiles*100))+' | '+str(round(faxSize/totSize*100))+' |')
f.write('')
f.write("""%CHART{name="bar1" table="Table1" type="bar" data="R4:C2..R4:C4" xaxis="R1:C2..R1:C4" legend="R4:C1" width="225" height="200" ymin="0" ymax="100" yaxis="on"}% """ )
f.close()

	  

