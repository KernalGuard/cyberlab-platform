# Feasibility spikes

Throwaway experiments that informed ADRs. **Not production code.** They were run on 2026-10-09 in an Ubuntu 24.04 x86-64 workspace as an unprivileged user (e2fsprogs 1.47.0, Sleuth Kit 4.12.1, dosfstools, mtools).

| Script | Question | Result | ADR |
|---|---|---|---|
| `ext4-fat-recovery-spike.sh` | Can we build ext4/FAT32 images with deleted files without root, and what does TSK recover? | Yes. ext4 deleted content was recoverable with `icat` (unrealistic vs. kernel deletion); FAT deletion artifacts looked realistic. | 0008 |
| `ext4-determinism-spike.sh` | Is the generated ext4 image byte-reproducible? | Yes, after pinning UUID/hash seed and normalizing inode timestamps (two runs, identical SHA-256). Normalizing unallocated inodes caused orphan-file noise. | 0007, 0008 |
| [`ext4-kernel-deletion/`](ext4-kernel-deletion/README.md) (2026-11-17) | Does a real kernel delete differently from `debugfs rm`, and can we reproduce it without root? (R-03) | Yes: the kernel zeroes the dirent and the extent map but leaves data. `ext4_kernel_delete.py` matches the kernel (dir block byte-identical, bitmaps identical), is byte-reproducible and fsck-clean. **R-03 resolved.** | 0008 |

Usage: `bash <script> <working-dir>` where `<working-dir>` contains `src/home/jdoe/Documents/`. Requires e2fsprogs, sleuthkit, dosfstools, mtools.
