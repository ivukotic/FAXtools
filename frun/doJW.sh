./frun -v --inDS=user.JordanWebster.UCNTUP.data12_8TeV.periodB.physics_Egamma.PhysCont.AOD.t0pro13_v01.j.v1_30b.120705192354 --exec "echo %IN | sed -e \"s/,/\n/g\" > input.txt; ./doRead.sh" \
--athenaTag=17.2.0 \
--noBuild \
--outputs=input.txt,ilija.txt \
--outDS=user.ivukotic.HCtestREWRITTEN.1 \
--site=ANALY_CERN_XROOTD
