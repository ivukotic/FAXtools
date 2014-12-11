#!/usr/bin/env python
import socket,time
MBPS=100

UDP_IP = "134.79.200.87"
UDP_PORT = 9931
interval=30
totout=0
totin=0
CT=int(time.time())
m0=' ver="v4.1.1" src="test.injection:1094" tos="'+str(CT)+'" pgm="xrootd" ins="anon" pid="12345" site="TEST">'
m1=""" <stats id="info"><host>"""+socket.gethostname().split('.')[0]+""".test.edu</host><port>1094</port><name>anon</name></stats>
<stats id="buff"><reqs>10</reqs><mem>10000</mem><buffs>10</buffs><adj>0</adj></stats>
<stats id="link"><num>8</num><maxn>8</maxn><tot>8</tot><in>"""
m2='</in><out>'
m3="""</out><ctime>0</ctime><tmo>34</tmo><stall>0</stall><sfps>0</sfps></stats>
<stats id="poll"><att>8</att><en>34</en><ev>34</ev><int>0</int></stats>
<stats id="proc"><usr><s>0</s><u>50000</u></usr><sys><s>0</s><u>50000</u></sys></stats>
<stats id="xrootd"><num>8</num><ops><open>51</open><rf>0</rf><rd>14</rd><pr>0</pr><rv>0</rv><rs>0</rs><wr>0</wr><sync>0</sync><getf>0</getf><putf>0</putf><misc>15</misc></ops><aio><num>0</num><max>0</max><rej>0</rej></aio><err>0</err><rdr>0</rdr><dly>47</dly><lgn><num>8</num><af>0</af><au>8</au><ua>0</ua></lgn></stats>
<stats id="ofs"><role>proxy server</role><opr>2</opr><opw>0</opw><opp>0</opp><ups>0</ups><han>3</han><rdr>0</rdr><bxq>0</bxq><rep>0</rep><err>0</err><dly>0</dly><sok>0</sok><ser>0</ser><tpc><grnt>0</grnt><deny>0</deny><err>0</err><exp>0</exp></tpc></stats>
<stats id="sched"><jobs>57</jobs><inq>0</inq><maxinq>2</maxinq><threads>12</threads><idle>0</idle><tcr>12</tcr><tde>0</tde><tlimr>0</tlimr></stats>
<stats id="sgen"><as>0</as><et>0</et><toe>"""

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "interval:", interval

for i in range(100):
    ET=int(time.time())
    ST=ET-10
    MESSAGE = '<statistics tod="'+str(ST)+'"'+m0+m1+str(totin)+m2+str(totout)+m3+str(ET)+'</toe></stats></statistics>'
    print i # ,"message:", MESSAGE
    time.sleep(interval)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    totin+=1024*1024*interval
    totout+=MBPS*1024*1024*interval
