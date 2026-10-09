set -e; cd "$1"; rm -f d.img
export E2FSPROGS_FAKE_TIME=1760000000 SOURCE_DATE_EPOCH=1760000000
find src -exec touch -h -d @1759000000 {} +
mkfs.ext4 -q -F -d src -U 11111111-2222-3333-4444-555555555555 -E hash_seed=11111111-2222-3333-4444-555555555555,root_owner=1000:1000 -O ^metadata_csum_seed d.img 16M
for i in 2 $(seq 11 20); do for f in ctime atime mtime crtime; do debugfs -w d.img -R "set_inode_field <$i> $f 20261001090000" 2>/dev/null; debugfs -w d.img -R "set_inode_field <$i> ${f}_extra 0" 2>/dev/null; done; done
F=/home/jdoe/Documents/payroll_q3.csv
for fld in atime ctime crtime; do debugfs -w d.img -R "set_inode_field $F $fld 20261003141500" 2>/dev/null; done
INO=$(debugfs -R "stat $F" d.img 2>/dev/null | awk '/^Inode:/{print $2}')
debugfs -w d.img -R "rm $F" 2>/dev/null
for fld in ctime dtime; do debugfs -w d.img -R "set_inode_field <$INO> $fld 20261005021700" 2>/dev/null; done
debugfs -w d.img -R "set_super_value wtime 20261005030000" 2>/dev/null
debugfs -w d.img -R "set_super_value lastcheck 20261001000000" 2>/dev/null
debugfs -w d.img -R "set_super_value mkfs_time 20261001000000" 2>/dev/null
sha256sum d.img
