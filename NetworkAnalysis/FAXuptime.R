hours<-720

library(rjson)

setEPS()
postscript(file = "FAXavailability.eps", width=7, height=2.5)
#png(file = "FAXavailability.png",width = 1024, height = 480, pointsize=6, res=240)
#pdf(file = "FAXavailability.pdf", width=7, height=2.5)
par(mfrow = c(1, 3))
par(mar=c(1,1.5,3,1.5) )

ur <- paste("http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?time=",hours,"&dateFrom=&dateTo=&site=AGLT2&sites=all&clouds=all&batch=1&columnid=", sep = "")

url <- paste(ur,"10083",sep="")
print(url)
document <- fromJSON(file = url, method = "C")
cvs = document["csvdata"]
a = cvs[[1]]

mMat <- do.call(rbind, a)
mMat <- mMat[, -c(1, 2, 5, 6, 7, 9, 11)]

mDF <- as.data.frame(mMat)
mDF$COLOR <- unlist(mDF$COLOR)
mDF$VOName <- unlist(mDF$VOName)
mDF$Time <- as.POSIXct(unlist(mDF$Time), format = "%Y-%m-%dT%H:%M:%S")
mDF$EndTime <- as.POSIXct(unlist(mDF$EndTime), format = "%Y-%m-%dT%H:%M:%S")
mDFsorted <- mDF[order(mDF$VOName, mDF$Time), ]

greentime <- 0;redtime <- 0; graytime <- 0
for (i in 1:nrow(mDFsorted)) {
	dt <- mDFsorted$EndTime[[i]] - mDFsorted$Time[[i]]
	if (mDFsorted$COLOR[[i]] == 3) {
		redtime <- redtime + dt
	}
	if (mDFsorted$COLOR[[i]] == 7) {
		graytime <- graytime + dt
	}
	if (mDFsorted$COLOR[[i]] == 5) {
		greentime <- greentime + dt
	}
}

tottime <- sum(mDFsorted$EndTime - mDFsorted$Time)

slices <- c(greentime, redtime, graytime)
lbls <- c("available", "unavailable", "offline")
pct <- round(slices/sum(slices) * 100)
#lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls, "\n", pct , "%", sep = "") # ad % to labels
pie(slices, labels = lbls, main = "Direct access availability", col = c("green", "red", "gray"))


url <- paste(ur,"10084",sep="")
print(url)
document <- fromJSON(file = url, method = "C")
cvs = document["csvdata"]
a = cvs[[1]]

mMat <- do.call(rbind, a)
mMat <- mMat[, -c(1, 2, 5, 6, 7, 9, 11)]

mDF <- as.data.frame(mMat)
mDF$COLOR <- unlist(mDF$COLOR)
mDF$VOName <- unlist(mDF$VOName)
mDF$Time <- as.POSIXct(unlist(mDF$Time), format = "%Y-%m-%dT%H:%M:%S")
mDF$EndTime <- as.POSIXct(unlist(mDF$EndTime), format = "%Y-%m-%dT%H:%M:%S")
mDFsorted <- mDF[order(mDF$VOName, mDF$Time), ]

greentime <- 0;redtime <- 0; graytime <- 0
for (i in 1:nrow(mDFsorted)) {
	dt <- mDFsorted$EndTime[[i]] - mDFsorted$Time[[i]]
	if (mDFsorted$COLOR[[i]] == 3) {
		redtime <- redtime + dt
	}
	if (mDFsorted$COLOR[[i]] == 7) {
		graytime <- graytime + dt
	}
	if (mDFsorted$COLOR[[i]] == 5) {
		greentime <- greentime + dt
	}
}

tottime <- sum(mDFsorted$EndTime - mDFsorted$Time)

slices <- c(greentime, redtime, graytime)
lbls <- c("available", "unavailable", "offline")
pct <- round(slices/sum(slices) * 100)
#lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls, "\n", pct , "%", sep = "") # ad % to labels
pie(slices, labels = lbls, main = "Upstream redirection", col = c("green", "red", "gray"))


url <- paste(ur,"10085",sep="")
print(url)
document <- fromJSON(file = url, method = "C")
cvs = document["csvdata"]
a = cvs[[1]]

mMat <- do.call(rbind, a)
mMat <- mMat[, -c(1, 2, 5, 6, 7, 9, 11)]

mDF <- as.data.frame(mMat)
mDF$COLOR <- unlist(mDF$COLOR)
mDF$VOName <- unlist(mDF$VOName)
mDF$Time <- as.POSIXct(unlist(mDF$Time), format = "%Y-%m-%dT%H:%M:%S")
mDF$EndTime <- as.POSIXct(unlist(mDF$EndTime), format = "%Y-%m-%dT%H:%M:%S")
mDFsorted <- mDF[order(mDF$VOName, mDF$Time), ]

greentime <- 0;redtime <- 0; graytime <- 0
for (i in 1:nrow(mDFsorted)) {
	dt <- mDFsorted$EndTime[[i]] - mDFsorted$Time[[i]]
	if (mDFsorted$COLOR[[i]] == 3) {
		redtime <- redtime + dt
	}
	if (mDFsorted$COLOR[[i]] == 7) {
		graytime <- graytime + dt
	}
	if (mDFsorted$COLOR[[i]] == 5) {
		greentime <- greentime + dt
	}
}

tottime <- sum(mDFsorted$EndTime - mDFsorted$Time)

slices <- c(greentime, redtime, graytime)
lbls <- c("available", "unavailable", "offline")
pct <- round(slices/sum(slices) * 100)
#lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls, "\n", pct , "%", sep = "") # ad % to labels
pie(slices, labels = lbls, main = "Downstream redirection", col = c("green", "red", "gray"))


dev.off()