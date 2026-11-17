#!/usr/bin/env python3
"""Delete a file from an ext4 image the way the Linux kernel does, without mounting.

`debugfs rm` frees the inode and blocks but leaves the inode's extent map, size and
the directory entry's name intact, so `icat` and `fls -d` recover deleted files
trivially (risk R-03). A kernel unlink+evict (observed on Linux 6.18) instead:

  inode:   links 0, size 0, i_blocks 0, extent header entries 0 and extent entries
           zeroed, mtime = ctime = dtime = deletion time; atime/crtime/mode/flags kept
  dirent:  previous entry's rec_len absorbs the entry and the entry's bytes
           (inode, rec_len, name_len, type, name) are zeroed
  blocks:  freed in the bitmap; DATA IS NOT WIPED (recoverable only by carving)

This tool runs `debugfs rm`, then applies the remaining differences with debugfs
`set_inode_field` and a direct directory-block patch with a recomputed metadata_csum.
Unprivileged; deterministic (no clock reads). Spike code for Lab 2 (2026-11-17).
"""

from __future__ import annotations

import argparse
import re
import struct
import subprocess
import sys

# --- crc32c (Castagnoli), raw update without pre/post inversion, as ext4 uses it ---
_T = []
for _i in range(256):
    _c = _i
    for _ in range(8):
        _c = (_c >> 1) ^ 0x82F63B78 if _c & 1 else _c >> 1
    _T.append(_c)


def crc32c(crc: int, data: bytes) -> int:
    for b in data:
        crc = _T[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc


def dbg(img: str, cmd: str, write: bool = False) -> str:
    args = ["debugfs"] + (["-w"] if write else []) + ["-R", cmd, img]
    p = subprocess.run(args, capture_output=True, text=True)
    if "debugfs:" in p.stderr and ("not found" in p.stderr or "Couldn't" in p.stderr):
        raise SystemExit(f"debugfs {cmd!r}: {p.stderr.strip()}")
    return p.stdout


def superblock(img: str) -> dict:
    with open(img, "rb") as f:
        f.seek(1024)
        sb = f.read(1024)
    log_bs = struct.unpack_from("<I", sb, 0x18)[0]
    incompat = struct.unpack_from("<I", sb, 0x60)[0]
    ro_compat = struct.unpack_from("<I", sb, 0x64)[0]
    uuid = sb[0x68:0x78]
    if incompat & 0x2000:                       # INCOMPAT_CSUM_SEED
        seed = struct.unpack_from("<I", sb, 0x270)[0]
    else:
        seed = crc32c(0xFFFFFFFF, uuid)
    return {"bs": 1024 << log_bs, "csum": bool(ro_compat & 0x400), "seed": seed}


def inode_number(img: str, path: str) -> int:
    m = re.search(r"Inode:\s+(\d+)", dbg(img, f"stat {path}"))
    if not m:
        raise SystemExit(f"{path}: not found in image")
    return int(m.group(1))


def generation(img: str, ino: int) -> int:
    m = re.search(r"Generation:\s+(\d+)", dbg(img, f"stat <{ino}>"))
    return int(m.group(1))


def dir_blocks(img: str, dir_ino: int) -> list[int]:
    return [int(b) for b in dbg(img, f"blocks <{dir_ino}>").split()]


def dir_tail_csum(sb: dict, dir_ino: int, gen: int, block: bytes) -> int:
    c = crc32c(sb["seed"], struct.pack("<I", dir_ino))
    c = crc32c(c, struct.pack("<I", gen))
    return crc32c(c, block[: sb["bs"] - 12])


def wipe_dirent(img: str, sb: dict, dir_ino: int, ino: int, name: bytes) -> bool:
    """Zero the (already unlinked) entry for `ino`/`name` in the parent directory."""
    bs, gen = sb["bs"], generation(img, dir_ino)
    want = struct.pack("<I", ino)
    with open(img, "r+b") as f:
        for blk in dir_blocks(img, dir_ino):
            f.seek(blk * bs)
            data = bytearray(f.read(bs))
            limit = bs - 12 if sb["csum"] else bs
            for off in range(0, limit - 8, 4):           # dirents are 4-byte aligned
                if data[off:off + 4] != want:
                    continue
                rec_len, name_len = struct.unpack_from("<HB", data, off + 4)
                if name_len != len(name) or bytes(data[off + 8:off + 8 + name_len]) != name:
                    continue
                if off == 0:
                    # first entry in the block: kernel keeps rec_len, clears inode and name
                    data[0:4] = b"\0" * 4
                    data[6:8 + name_len] = b"\0" * (2 + name_len)
                else:
                    span = rec_len if 8 <= rec_len <= limit - off else (8 + name_len + 3) & ~3
                    data[off:off + span] = b"\0" * span
                if sb["csum"]:
                    struct.pack_into("<I", data, bs - 4, dir_tail_csum(sb, dir_ino, gen, bytes(data)))
                f.seek(blk * bs)
                f.write(data)
                return True
    return False


def kernel_delete(img: str, path: str, when: str) -> None:
    """`when` is a debugfs time string, e.g. 20261005021700 (UTC)."""
    sb = superblock(img)
    parent, name = path.rsplit("/", 1)
    dir_ino, ino = inode_number(img, parent or "/"), inode_number(img, path)
    dbg(img, f"rm {path}", write=True)
    fields = [("size", "0"), ("blocks", "0"), ("block[0]", "62218"),   # 0xF30A magic, 0 entries
              ("mtime", when), ("ctime", when), ("dtime", when),
              ("mtime_extra", "0"), ("ctime_extra", "0")]
    fields += [(f"block[{i}]", "0") for i in range(3, 15)]
    for fld, val in fields:
        dbg(img, f"set_inode_field <{ino}> {fld} {val}", write=True)
    if not wipe_dirent(img, sb, dir_ino, ino, name.encode()):
        raise SystemExit(f"{path}: directory entry not found after rm")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("image")
    ap.add_argument("path", nargs="+", help="absolute path(s) inside the image")
    ap.add_argument("--when", required=True, help="deletion time, YYYYMMDDHHMMSS (UTC)")
    ap.add_argument("--check-csum", action="store_true",
                    help="verify this tool's dir checksum against an existing image (no changes)")
    a = ap.parse_args(argv)
    if a.check_csum:
        sb = superblock(a.image)
        for p in a.path:
            d = inode_number(a.image, p)
            for blk in dir_blocks(a.image, d):
                with open(a.image, "rb") as f:
                    f.seek(blk * sb["bs"])
                    data = f.read(sb["bs"])
                ok = struct.unpack_from("<I", data, sb["bs"] - 4)[0] == dir_tail_csum(sb, d, generation(a.image, d), data)
                print(f"{p} block {blk}: csum {'OK' if ok else 'MISMATCH'}")
        return 0
    for p in a.path:
        kernel_delete(a.image, p, a.when)
    return 0


if __name__ == "__main__":
    sys.exit(main())
