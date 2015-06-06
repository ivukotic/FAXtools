flume-ng agent -c flume -f /home/ivukotic/FAXtools/FAXconfiguration/FAX_summary_collector.properties -n ucAgent -C '/home/ivukotic/FAXtools/FAXconfiguration'  -Dflume.monitoring.type=http -Dflume.monitoring.port=34549

