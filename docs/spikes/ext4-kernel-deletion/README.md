# R-03 spike: kernel-realistic ext4 deletion (Lab 2)

**Question.** Generated ext4 images (ADR-0008) delete files with `debugfs rm`, which leaves deleted files trivially recoverable (`icat` returns the whole file, `fls -d` shows the name). Does a real kernel behave differently, and can we reproduce the kernel's on-disk result without root?

**Answer.** Yes, and yes. A real kernel wipes the directory entry and the inode's block map but leaves the data blocks. `ext4_kernel_delete.py` reproduces the kernel result in user space, byte-reproducibly, and the result passes `e2fsck`.

**Status:** run 2026-11-17 in the cloud workspace: Linux 6.18.44 (loop mount, real kernel), e2fsprogs 1.47.0, Sleuth Kit 4.12.1, Python 3.13. Spike code, not the Lab 2 generator.

## Method

1. `kernel_ref.sh`: `mkfs.ext4` (default features incl. `metadata_csum`, 4 KiB blocks), **loop-mount**, write four files (one 42 KB / 11-block CSV), unmount, keep a copy (`*-before.img`), mount again, `rm` two files with the kernel, unmount.
2. Same "before" image: delete the same files with `debugfs rm` and, separately, with `ext4_kernel_delete.py`.
3. Compare with Sleuth Kit (`fls -d`, `istat`, `icat`, `blkls`), raw directory blocks (`blkcat`), raw inodes (`debugfs inode_dump`), `e2fsck -fn` and a block-by-block image diff.

## Results

| Attribute after deletion | Real kernel (6.18) | `debugfs rm` | `ext4_kernel_delete.py` |
|---|---|---|---|
| Inode allocated / links | no / 0 | no / 0 | no / 0 |
| `size`, `i_blocks` | **0, 0** | unchanged (42180) | **0, 0** |
| Extent header entries / extent records | **0 / zeroed** | unchanged | **0 / zeroed** |
| mtime, ctime | **= deletion time** | unchanged | **= deletion time** |
| dtime | deletion time | deletion time (from the clock) | deletion time (given) |
| atime, crtime, mode, flags | unchanged | unchanged | unchanged |
| Directory entry | previous `rec_len` absorbs it; **entry bytes zeroed (name gone)** | previous `rec_len` absorbs it; name left intact | **byte-identical to kernel** |
| `fls -d` shows | `$OrphanFiles/OrphanFile-16` (no name) | `donors_export.csv` | same as kernel |
| `icat` recovers | **0 bytes** | whole file | **0 bytes** |
| Data blocks | freed, **content intact** | freed, content intact | freed, content intact |
| Carving `blkls \| grep` | 800/800 records found | 800/800 | 800/800 |
| Block/inode bitmaps, group descriptors | — | — | **identical to kernel** |
| `e2fsck -fn` | clean | clean | clean |
| Byte-reproducible | no (clock, journal) | no (clock) | **yes** (two runs, same SHA-256) |

Remaining differences between the kernel image and the emulated image (13 of 8,192 blocks):

- **Inode nanosecond fields and checksum** (`*_extra`): the tool sets them to 0 for determinism. The first 128 bytes of the inode are identical.
- **Superblock** (block 0): mount count, write/mount times. The generator sets these explicitly.
- **Journal** (blocks 11–33): the kernel's journal still holds **copies of the pre-deletion inode table block (with the old extent map) and the pre-deletion directory block (with both filenames)**. Generated images have a clean journal.

## Implications for Lab 2

1. **R-03 is resolved** for the documented attributes: the generator must call `ext4_kernel_delete.py` (or its library form) instead of `debugfs rm`.
2. **Realistic lesson:** on a modern Linux system, a deleted file's *name* and *block map* are gone from the file system. Students recover the *content* by carving unallocated space (`blkls`, `grep -a`, `blkcat`), and the *name and time* from other artifacts: `.bash_history`, the deletion time (`dtime`) of the orphan inode, the USB stick's FAT directory (where deleted names survive with the first character replaced).
3. **Journal recovery** (`debugfs logdump`, ext4magic) is how examiners recover names and extents on real systems. Our images do not contain it. Options: (a) document as a synthetic-vs-real difference (default), or (b) a later generator feature that writes a deterministic journal transaction, for a graduate challenge.
4. Normalising timestamps on **unallocated** inodes creates `$OrphanFiles` noise (seen again here, inodes 18–20). The generator must touch only allocated inodes.
5. Kernel behaviour differs by version: older kernels left the deleted name in the directory entry. The student guide should say "on the Linux version this image imitates".

## Files

| File | Purpose |
|---|---|
| `kernel_ref.sh` | Builds the kernel reference (needs root + loop devices) |
| `ext4_kernel_delete.py` | User-space kernel-like deletion: `debugfs rm` + inode fields + directory-entry wipe with recomputed `metadata_csum` (`--check-csum` validates the checksum code against a kernel-made image) |
| `build_emu.sh` | Determinism check: builds the same image twice with fixed times, applies the deletion |
