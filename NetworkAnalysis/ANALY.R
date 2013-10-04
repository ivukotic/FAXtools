
library(psych)

load("cleanFAX.data")
print("FAX measurements:")
print(describe(cleanedFAX$rate))

load("cleanFTS.data")
names<-c("small","medium","large")
j<-1
cc             <- strsplit(as.vector(cleaned[[j]]$link),"_to_")
source         <- unlist(cc)[2*(1:length(cleaned[[j]]$link))-1]
destination    <- unlist(cc)[2*(1:length(cleaned[[j]]$link))  ]
cleaned[[j]]$source<-as.list(source)
cleaned[[j]]$destination <-as.list(destination)

print ("FTS measurements:")
print(describe(cleaned[[j]]$rate))

#removing links not measured by both FAX and FTS 
SS2=subset(cleanedFAX, cleanedFAX$link %in% cleaned[[j]]$link, select=c(link, rate, date, source, destination) )
SS2$link <- factor(SS2$link)

print(length(SS2$rate))
SS1=subset(cleaned[[j]], cleaned[[j]]$link %in% cleanedFAX$link, select=c(link, rate, date, source, destination) )
SS1$link <- factor(SS1$link)
print(length(SS1$rate))
SS2["mod"]<-"FAX"
SS1["mod"]<-"FTS"

FF<-rbind(SS2,SS1)

print("combined length")
print(length(FF$rate))

# point-biserial correlation
library(ltm)
biserial.cor(FF$rate, FF$mod)

# this should create sumup's of all three measurements

FAXLink<-split(SS2, SS2$link)
FTSLink<-split(SS1, SS1$link)


par(mfrow = c(4, 2))
par(plt=c(0.2,0.95,0.2,0.8) )
for (r in 1:8){
	fts<-FTSLink[[r]]
	fax<-FAXLink[[r]]
	maintitle<-paste(paste(fts$source[[1]],"to", fts$destination[[1]]))
	yl=c(min(fts$rate,fax$rate),max(fts$rate,fax$rate))
	xl=c(min(fts$date,fax$date),max(fts$date,fax$date))
	
	if (T){	# just values
		plot(x=fts$date, y= fts$rate,  main=maintitle, xlim=xl, ylim=yl, xlab='date', ylab='rate [MB/s]', type="l", col="blue")
		par(new=T)
		plot(x= fax$date, y= fax$rate, axes=F, type="l", col="red")
		par(new=F)
	}
	
	if (F){
		# distributions
		dfts<-diff(fts$rate)
		dfax<-diff(fax$rate)
		hist(dfts, prob=T, main=maintitle, xlim=c(min(dfts,dfax), max(dfts,dfax)), col="blue")
		x<-seq(min(dfts,dfax),max(dfts,dfax),length=100)
		y<-dnorm(x,mean(dfts),sd(dfts))
		lines(x,y,col="blue")
		par(new=T)
		hist(dfax, prob=T, main=maintitle, axes=F)
		y1<-dnorm(x,mean(dfax),sd(dfax))
		lines(x,y1,col="red")
		par(new=F)
	}	
	
	print("FTS:")
	print (fts$rate)
	print("FAX:")
	print(fax$rate)
	print("================================")
}
# this should check correlations between pairs of measurements (3 in total)

