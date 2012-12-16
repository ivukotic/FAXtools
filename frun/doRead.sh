 cat input.txt |
while read line
do
echo $line
root -q -b "read.C++(\"$line\",\"physics\",100,30)"
done 
