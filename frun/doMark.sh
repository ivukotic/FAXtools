./frun -v --inDS=group.phys-higgs.periodA.physics_Egamma.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodA.physics_Muons.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodB.physics_Egamma.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodB.physics_Muons.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodC.physics_Egamma.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodC.physics_Muons.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodD.physics_Egamma.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodD.physics_Muons.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodE.physics_Muons.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/,group.phys-higgs.periodE.physics_Egamma.PhysCont.NTUP_SMWZ.grp13_v01_p1067_HWW_2.07r525219_lvqq_0.04_0_Nominal/ --exec "echo %IN | sed -e \"s/,/\n/g\" > input.txt; ./doRead.sh" \
--athenaTag=17.2.0 \
--noBuild \
--outputs=input.txt,ilija.txt \
--outDS=user.ivukotic.HCtestREWRITTEN.2 \
--site=ANALY_CERN_XROOTD
