# ADR-0008: Generate disk images in user space (no loop mounts)

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** SEC-01, SEC-02, FR-E-02, NFR-05

## Context
The conventional way to build a forensic test image (create file → `mount -o loop` → copy and delete files → unmount) requires root and `CAP_SYS_ADMIN`, which violates the least-privilege baseline and fails in CI and rootless environments.

## Decision
Build file-system images entirely in user space:
- **ext4:** `mkfs.ext4 -d <tree>` with fixed UUID and hash seed; `debugfs -w` to set timestamps, delete files, and normalize inode metadata.
- **FAT32:** `mkfs.vfat -C` with fixed volume ID; `mtools` (`mcopy`, `mdel`, `mattrib`) to populate and delete.
- **Kernel-realism step:** after `debugfs rm`, explicitly clear the deleted inode's extent/block fields so recovery behavior matches deletion by the Linux kernel; validated against a reference image produced in a VM (Week 4).

## Evidence — feasibility spike, 2026-10-09 (Ubuntu 24.04 x86-64, e2fsprogs 1.47.0, TSK 4.12.1, unprivileged user)
- ✅ Image created, timestamps backdated, a file deleted, no root or mounts.
- ✅ `fls -r -d` lists the deleted entry; `istat` shows the set times and deletion time.
- ⚠️ `icat` recovered the deleted content directly: `debugfs rm` does **not** clear extents the way kernel deletion does → the kernel-realism step is needed.
- ✅ Byte-reproducible across two builds after normalizing *allocated* inodes' timestamps (including `_extra` nanosecond fields).
- ⚠️ Touching *unallocated* inodes created `$OrphanFiles` noise → normalize allocated inodes only.
- ✅ FAT32 via mtools: deleted entry visible with first character replaced (`_ist.txt`).
- `debugfs` time arguments are interpreted as **UTC**; generators work in UTC throughout.
Spike scripts: `docs/spikes/`. **Not yet tested inside the Debian 13 image** (Debian 13 ships a newer e2fsprogs; exact version to be pinned) — to be done in Week 4.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Loop mount in privileged container | Real kernel semantics | Privileged; fails on Docker Desktop/CI policies | Security baseline |
| Build in a VM, ship static images | Highest realism | Not seedable per student; heavy build | Used only as a realism *reference* |
| `fuse2fs` | Kernel-like through libext2fs | Needs `/dev/fuse` + `SYS_ADMIN` | Same privilege problem |

## Consequences
+ Generation runs in CI and in any unprivileged container. − Must maintain an explicit list of kernel-vs-debugfs differences and test it.
