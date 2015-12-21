flume-ng agent -c flume -f /home/ivukotic/FAXtools/CostCollector/CostCollector.properties -n ucAgent -C '/home/ivukotic/FAXtools/CostCollector'  -Dflume.monitoring.type=http -Dflume.monitoring.port=34545

