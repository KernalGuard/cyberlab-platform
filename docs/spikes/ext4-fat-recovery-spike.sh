set -e
cd "$1"
echo "Quarterly payroll export - CONFIDENTIAL" > src/home/jdoe/Documents/payroll_q3.csv
echo "meeting notes" > src/home/jdoe/Documents/notes.txt
export E2FSPROGS_FAKE_TIME=1760000000
mkfs.ext4 -q -F -d src -E root_owner=1000:1000 -U 11111111-2222-3333-4444-555555555555 -E hash_seed=11111111-2222-3333-4444-555555555555 disk.img 16M
debugfs -w disk.img -R "set_inode_field /home/jdoe/Documents/payroll_q3.csv mtime 20261003141500" 2>/dev/null
debugfs -w -R "rm /home/jdoe/Documents/payroll_q3.csv" disk.img 2>/dev/null
echo "--- fls -r -d (deleted entries)"; fls -r -d disk.img
INODE=$(fls -r -d disk.img | grep payroll | sed -E 's/.*\* ([0-9]+).*/\1/;s/[^0-9].*//')
echo "--- istat $INODE"; istat disk.img $INODE | sed -n '1,25p' | grep -E "Allocated|Modified|Size|Direct|Extent|^[0-9]" 
echo "--- icat"; icat disk.img $INODE | head -2 || true
echo "--- blkls+strings (carving)"; blkls disk.img | strings | grep -i payroll || true
sha256sum disk.img
# FAT32 USB via mtools, no mount
mkfs.vfat -C -F 32 -i 1A2B3C4D -n EVIDUSB usb.img 40000 >/dev/null
echo "exfil list" > list.txt; mcopy -i usb.img list.txt ::/list.txt; mcopy -i usb.img src/home/jdoe/Documents/notes.txt ::/notes.txt; mdel -i usb.img ::/list.txt
echo "--- FAT fls -d"; fls -f fat32 -r -d usb.img; I=$(fls -f fat32 -r -d usb.img | grep -i list | sed -E 's/.*\* ([0-9]+).*/\1/;s/[^0-9].*//'); echo "--- FAT icat"; icat -f fat32 usb.img $I
