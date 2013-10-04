toEPS<-FALSE
reload<-FALSE
days<-5

library(rjson)
library(psych)

if(reload){
	today <- Sys.Date()
	format(today, format="%y-%m-%d")
	from=today-days
	format(from, format="%y-%m-%d")
	url=paste('http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?batch=1&time=custom&dateFrom=',as.character(from),'&dateTo=',as.character(today),'&columnid=10091',sep="")
	print(url)
	document <- fromJSON(file=url,method='C')
	cvs=document["csvdata"]

	#this is a list
	a=cvs[[1]]
	length(a)
	save(a,file="localCopyFAX.data")
	print("loading done")
}

if (reload){
	load("localCopyFAX.data")

	#transforms it into matrix
	mMat <- matrix(unlist(a), ncol=9, byrow=TRUE)

	#removes columns 1,2,3,6,7
	mMat <- mMat[,-c(1,2,3,6,7)]

	#transforms matrix into data.frame
	mDF <- as.data.frame(mMat)
	colnames(mDF)[1] <- 'link'
	colnames(mDF)[2] <- 'rate'
	colnames(mDF)[3] <- 'date'
	mDF[,2]<-as.numeric(mMat[,2])
	mDF[,3] <- as.POSIXct(mDF[,3],format="%Y-%m-%dT%H:%M:%S")
	mDF[,4] <- as.POSIXct(mDF[,4],format="%Y-%m-%dT%H:%M:%S")

	#orders it first over link and than over date
	mDFsorted <- mDF[order(mDF$link,mDF$date),]
	
	#prints first 10 rows
	head(mDFsorted,10)
	
	#removing rows with NA in source or destination
	for(i in 1:nrow(mDFsorted)){ 
		ss<-strsplit(as.vector(mDFsorted $link[[i]]),"_to_"); 
		if(length(ss[[1]])==1) {
			print(paste("problem! dropping: ", mDFsorted $link[[i]]))
			mDFsorted[i, "rate" ]<-0
		}
	}
	
	#removing rows with 0 rate
	cleanedFAX<-I(data.frame(mDFsorted[mDFsorted$rate>0,]))
	
	cc       <- strsplit(as.vector(cleanedFAX$link),"_to_")
	source         <- unlist(cc)[2*(1:length(cleanedFAX$link))-1]
	destination    <- unlist(cc)[2*(1:length(cleanedFAX$link))  ]
    
	cleanedFAX$source<-as.list(source)
	cleanedFAX$destination <-as.list(destination)
	
	save(cleanedFAX,file="cleanFAX.data")
}

	load("cleanFAX.data")
	

	uSources<-sort(unlist(unique(cleanedFAX$source)))
	uDestinations<-sort(unlist(unique(cleanedFAX$destination)))
	
	print ("all measurements describing rate:")
	print(describe(cleanedFAX$rate))


	nme<-aggregate(rate~link, data=cleanedFAX, FUN="length")
	print(paste("average measurements per link:",mean(nme$rate)))	
	
	me <- aggregate(rate~link, data=cleanedFAX, FUN="mean")
	print ("per link:")
	print (describe(me$rate))
	print (paste("total bandwidth:",sum(me$rate)))
	
	if(toEPS){
		setEPS()
		postscript(file = "FAX.eps")
	}
	
	 par(mar=c(1,1.5,3,1.5) )
	 par(mfrow = c(2, 1))
	 plot (x=c(1:length(me$link)),y=me$rate,main="FAX measurements (100MB files)", xlab="link number", ylab="MB/s",type="h")
    if (toEPS) {
    	hist(me$rate,ylab="count", xlab="rate MB/s")
    	dev.off()
    }else{
	    hist(me$rate,main="FAX measurements" ,ylab="count", xlab="rate MB/s")	
    }
    
    
    if(toEPS) 	postscript(file = "FAX_rates_pie.eps")
	 par(mfrow = c(1, 1))
	 par(mar=c(1,1.5,1,1.5) )
	 slices<-hist(me$rate,breaks=c(0,1,10,100,15000),  plot=FALSE)$counts
	 lbls <- c("< 1 MB/s", "1 - 10 MB/s", "10 - 100 MB/s",">100 MB/s")
	 lbls <- paste(lbls, paste("\n",slices," links",sep=""))
    if(toEPS){ 
		 pie (slices, labels = lbls, col = c("red", "gray", "blue", "green"))
    	 dev.off()
 	}else{
	 	pie (slices, labels = lbls,main="FAX rates (100MB files)", col = c("red", "gray", "blue", "green"))	
 	}
	
	ma<-aggregate(rate~unlist(source) + unlist(destination), data=cleanedFAX, FUN="mean")	
	m <- matrix(NA, nrow = length(uSources), ncol = length(uDestinations), byrow = FALSE, dimnames = list(uSources, uDestinations))
	for(i in 1:nrow(ma)){	 
		m[rownames(m)==ma[i,1],colnames(m)==ma[i,2]] <- ma[i,3] 
	} #these column indices not checked
	
	print(m[1:4,1:4])
	
	if(toEPS) postscript(file = "FAXmatrix.eps")
	par(mfrow = c(1, 1))
	par(plt=c(0.2,0.98,0.2,0.90) )
	
	image(c(1:length(uSources)), c(1:length(uDestinations)), m, # xlim=c(0,86),ylim=c(0,86),
		#col =topo.colors(12), #c("blue","green","red")   #key.axes = axis(4, seq(0, 200, by = 10)),
		col=c("red","blue","green","yellow"),
		breaks=c(0,1,10,100,1000),
		axes=FALSE,xlab="Sources",ylab="Destinations",)#main="FAX measurements (100MB files)")
	
	axis(1,at=c(1:length(uSources)),labels=uSources, cex.axis=0.4,las=2)
	axis(2,at=c(1:length(uDestinations)),labels= uDestinations, cex.axis=0.4,las=2)
	if(toEPS) dev.off()
	 
	par(mfrow = c(4, 2))
	par(plt=c(0.2,0.95,0.2,0.8) )
	#splits per link
	aLink<-split(cleanedFAX, cleanedFAX$link)
#	for (r in 2:9)
#		plot(x=aLink[[r]]$date, y=aLink[[r]]$rate,  main=paste(paste(aLink[[r]]$source[[1]],"to",aLink[[r]]$destination[[1]])), xlab='date', ylab='rate [MB/s]', type="l", col="blue")
	

