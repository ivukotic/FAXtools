./frun -v --inDS=user.ilijav.HCtest.1 --exec "echo %IN | sed -e \"s/,/\n/g\" > input.txt; ./doRead.sh" \
--athenaTag=17.2.0 \
--noBuild \
--outputs=input.txt,ilija.txt \
--outDS=user.ivukotic.HCtestREWRITTEN.1 \
--site=ANALY_CERN_XROOTD
