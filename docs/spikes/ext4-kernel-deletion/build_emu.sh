set -e; out=$1; rm -rf src_$out $out; mkdir -p src_$out/home/jdoe/Documents
printf 'meeting notes\n' > src_$out/home/jdoe/Documents/notes.txt
python3 -c "
import sys; sys.stdout.write(''.join(f'DONOR-{i:05d},Name{i},name{i}@example.org,212-555-01{i%100:02d}\n' for i in range(800)))" > src_$out/home/jdoe/Documents/donors_export.csv
printf 'after\n' > src_$out/home/jdoe/Documents/zz_after.txt
export E2FSPROGS_FAKE_TIME=1791000000
find src_$out -exec touch -h -d @1790000000 {} +
mkfs.ext4 -q -F -d src_$out -U 11111111-2222-3333-4444-555555555555 -E hash_seed=11111111-2222-3333-4444-555555555555,root_owner=1000:1000 -O ^metadata_csum_seed $out 32M
N=$(debugfs -R "stats" $out 2>/dev/null | awk '/^Inode count/{print $3}')
for i in 2 $(seq 11 20); do for f in ctime atime mtime crtime; do debugfs -w $out -R "set_inode_field <$i> $f 20261001090000" 2>/dev/null; debugfs -w $out -R "set_inode_field <$i> ${f}_extra 0" 2>/dev/null; done; done
python3 ext4_kernel_delete.py $out /home/jdoe/Documents/donors_export.csv --when 20261005021700
for k in wtime lastcheck mkfs_time; do debugfs -w $out -R "set_super_value $k 20261005030000" 2>/dev/null; done
