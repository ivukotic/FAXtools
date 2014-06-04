import urllib2,json

req = urllib2.Request("http://atlas-agis-api.cern.ch/request/site/query/list/?json&vo_name=atlas&state=ACTIVE", None)
opener = urllib2.build_opener()
f = opener.open(req, timeout=20)
res=json.load(f)
for s in res:
	if(s["name"]!=s["rc_site"]):
		print s["name"],s["rc_site"]
