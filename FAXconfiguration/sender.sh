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
# delete it, then create it 
#   curl -XDELETE aianalytics01.cern.ch:9200/_template/fax_summary_redirectors_template
#   
#   curl -XPOST 'http://aianalytics01.cern.ch:9200/_template/fax_summary_redirectors_template' -d '{
#       "template" : "fax_summary_redirectors*",
#       "settings" : {  "number_of_shards" : 3, "number_of_replicas" : 2 },
#       "mappings" : {
#           "summary_redirectors" : {
#               "_source" : { "enabled" : true },
#               "properties" : {
#                   "@fields.redirector" : { "type" : "string", "index" : "not_analyzed" },
#                   "@fields.connections" : { "type" : "integer", "index" : "analyzed" },
#                   "@fields.ctime" : { "type" : "integer", "index" : "not_analyzed" },
#                   "@fields.delays" : { "type" : "integer", "index" : "not_analyzed" },
#                   "@fields.timeouts" : { "type" : "integer", "index" : "not_analyzed" },
#                   "@fields.redirects" : { "type" : "integer", "index" : "not_analyzed" },
#                   "@fields.errors" : { "type" : "integer", "index" : "not_analyzed" },
#                   "@fields.type" : { "type" : "string", "index" : "not_analyzed" }
#               }
#           }
#       }
#   }'
#

# delete index:
# curl -XDELETE 'http://aianalytics01.cern.ch:9200/fax_summary_redirectors_2015-06-25'

