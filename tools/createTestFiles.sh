mkdir user.ivukotic.xrootd.$1
cd user.ivukotic.xrootd.$1
dd if=/dev/zero of=user.ivukotic.xrootd.$1-1M  bs=1M  count=1
dd if=/dev/zero of=user.ivukotic.xrootd.$1-10M  bs=10M count=1
dd if=/dev/zero of=user.ivukotic.xrootd.$1-100M  bs=100M  count=1
dd if=/dev/zero of=user.ivukotic.xrootd.$1-1G  bs=1G  count=1
cd ..
dq2-put -L MWT2_UC_LOCALGROUPDISK -a -s user.ivukotic.xrootd.$1  user.ivukotic.xrootd.$1
dq2-freeze-dataset user.ivukotic.xrootd.$1
