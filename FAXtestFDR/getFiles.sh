export STORAGEPREFIX=root://fax.mwt2.org/

 cat inputDS_SMWZ.txt |
while read line
do
echo $line
dq2-list-files -p $line >> inputFiles.txt
#root -q -b "read.C++(\"$line\",\"physics\",100,30)"
done 
