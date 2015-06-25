cd /home/ivukotic/FAXtools/FAXconfiguration/t
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
source ${ATLAS_LOCAL_ROOT_BASE}/packageSetups/atlasLocalFAXSetup.sh --faxtoolsVersion ${faxtoolsVersionVal}
voms-proxy-init -valid 24:0 -voms atlas -pwstdin < /home/ivukotic/gridlozinka.txt
../FAX_summary_collector.py > sender.log 2>&1

##### flume sink is set like this:
# faxAgent.sinks.ESFAXredirectorsOut.indexName=fax_summary_redirectors
# faxAgent.sinks.ESFAXredirectorsOut.indexType=summary_redirectors

#####  ES template is like this
#   
#   curl -XPOST 'http://aianalytics01.cern.ch:9200/_template/fax_summary_redirectors_template' -d '{
#       "template" : "fax_summary_redirectors*",
#       "settings" : {  "number_of_shards" : 3, "number_of_replicas" : 2 },
#       "mappings" : {
#           "summary_redirectors" : {
#               "_source" : { "enabled" : true },
#               "properties" : {
#                   "redirector" : { "type" : "string", "index" : "not_analyzed" },
#                   "connections" : { "type" : "integer", "index" : "analyzed" },
#                   "ctime" : { "type" : "integer", "index" : "analyzed" },
#                   "delays" : { "type" : "integer", "index" : "analyzed" },
#                   "timeouts" : { "type" : "integer", "index" : "analyzed" },
#                   "redirects" : { "type" : "integer", "index" : "not_analyzed" },
#                   "errors" : { "type" : "integer", "index" : "not_analyzed" },
#                   "timestamp":{ "type": "date"}
#               }
#           }
#       }
#   }'
#
# delete it 
# curl -XDELETE aianalytics01.cern.ch:9200/_template/fax_summary_redirectors_template


