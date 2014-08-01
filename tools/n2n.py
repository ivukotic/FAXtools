import sys
import hashlib
m = hashlib.md5()
#print sys.argv[1]
s=sys.argv[1].split(':')[0]
s=s.replace('/','.')
n=sys.argv[1].split(':')[1]
#print 'scope',s
#print 'name',n
m.update(s+":"+n)
r=m.hexdigest()
print "rucio/"+s.replace('.','/')+"/"+m.hexdigest()[0:2]+'/'+m.hexdigest()[2:4]+'/'+n

