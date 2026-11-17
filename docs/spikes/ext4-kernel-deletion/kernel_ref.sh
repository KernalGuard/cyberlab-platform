#!/bin/bash
# Build an ext4 image, write files and delete one with the REAL kernel (loop mount).
set -e
img=${1:-kref.img}
rm -f $img; truncate -s 32M $img
mkfs.ext4 -q -F -U 11111111-2222-3333-4444-555555555555 $img
mkdir -p mnt; mount -o loop $img mnt
mkdir -p mnt/home/jdoe/Documents
printf 'meeting notes\n' > mnt/home/jdoe/Documents/notes.txt
# multi-block file with recognisable content (~40 KiB, 10 blocks)
python3 -c "
import sys
sys.stdout.write(''.join(f'DONOR-{i:05d},Name{i},name{i}@example.org,212-555-01{i%100:02d}\n' for i in range(800)))" > mnt/home/jdoe/Documents/donors_export.csv
printf 'small secret\n' > mnt/home/jdoe/Documents/small.txt
printf 'after\n' > mnt/home/jdoe/Documents/zz_after.txt
sync; umount mnt
cp $img ${img%.img}-before.img
mount -o loop $img mnt
rm mnt/home/jdoe/Documents/donors_export.csv mnt/home/jdoe/Documents/small.txt
sync; umount mnt
