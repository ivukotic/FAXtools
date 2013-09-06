library(rjson)
today <- Sys.Date()
format(today, format="%y-%m-%d")
from=today-5
format(from, format="%y-%m-%d")
url=paste('http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?batch=1&time=custom&dateFrom=',as.character(from),'&dateTo=',as.character(today),'&columnid=10091',sep="")
document <- fromJSON(file=url,method='C')
cvs=document["csvdata"]
a=cvs[[1]]
m <- matrix(unlist(a), ncol=9, byrow=TRUE)
m <- m[,-c(1,2,3,6,7)]
md <- as.data.frame(m)
colnames(md)[1] <- 'link'
colnames(md)[2] <- 'rate'
colnames(md)[3] <- 'date'
md[,3] <- as.POSIXct(md[,3],format="%Y-%m-%dT%H:%M:%S")
md[,4] <- as.POSIXct(md[,4],format="%Y-%m-%dT%H:%M:%S")
md[,2] <- as.numeric(md[,2])
md.sort1 <- md[order(md$link,md$date),]
head(md.sort1,10)
a=split(md.sort1,md.sort1$link)
a$`AGLT2_to_BNL-OSG2` <- droplevels(a$`AGLT2_to_BNL-OSG2`)
plot(x=a$`AGLT2_to_BNL-OSG2`$date, y=a$`AGLT2_to_BNL-OSG2`$rate,  main='AGLT2_to_BNL-OSG2', xlab='date', ylab='rate [MB/s]', type="l", col="blue")
length(a)
aggregate(rate~link,data=md.sort1, FUN="length")
me <- aggregate(rate~link,data=md.sort1, FUN="mean")
aggregate(rate~link,data=md.sort1, FUN="sd")
plot (x=me$link,y=me$rate)

#by( md.sort1, md.sort1[['link']], function( df ){ return (df)})
