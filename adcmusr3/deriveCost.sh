DATE_FROM="2013-06-08"
DATE_TO="2013-06-10"
SRC_METRIC_ID=10096

curl -H 'Accept: application/json' -H 'Content-Type: application/json' "http://dashb-atlas-ssb.cern.ch/dashboard/request.py/getplotdata?batch=1&time=custom&dateFrom=${DATE_FROM}&dateTo=${DATE_TO}&columnid=${SRC_METRIC_ID}" -o ${SRC_METRIC_ID}.json 2>/dev/null

