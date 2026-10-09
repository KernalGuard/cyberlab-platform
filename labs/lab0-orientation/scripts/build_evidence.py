#!/usr/bin/env python3
"""Build the Lab 0 practice evidence deterministically.

Lab 0 is an orientation lab with a single public dataset (no per-student
variants, no secrets), so this generator lives in the public repository.

Scenario: the owner of "Harbor Point Bakery" (a fictional business) received
emails about password resets she did not request. She copied a few files from
the shop computer to a USB stick and sent them, with a list of hashes she
computed, to an IT consultant. Students practise basic handling of that data.

Teaching points embedded in the data:
  * documents/report.txt is really a ZIP archive  -> the `file` command, magic bytes
  * images/storefront.png is a real PNG           -> magic bytes vs. extension
  * logs/auth.log has failed logins from one IP   -> grep, counting, pipes
  * transfer/sender_hashes.sha256 disagrees with one received file (budget.csv)
                                                   -> hashing, integrity, documentation
  * MANIFEST.sha256 describes the evidence exactly as distributed -> verify

All names, addresses and data are fictional. IPs come from RFC 5737 documentation
ranges and RFC 1918 private space; domains use the reserved .example TLD.

Usage:  python3 build_evidence.py <output_dir>
The output is byte-identical on every run and platform (checked by tests).
"""

from __future__ import annotations

import hashlib
import io
import struct
import sys
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "platform" / "lib"))
from cyberlab_common.manifest import write_manifest  # noqa: E402

FIXED_ZIP_TIME = (2026, 9, 28, 16, 42, 10)

CASE_BRIEF = """\
CASE BRIEF — PRACTICE EVIDENCE (Lab 0)
=====================================
Client:      Harbor Point Bakery (fictional)
Contact:     M. Alvarez, owner
Received:    2026-09-30 via USB copy, plus a hash list e-mailed by the client
Request:     The client received password-reset e-mails she did not request and
             wants to know whether anyone tried to access the shop computer.

Items:
  documents/meeting-notes.txt   Notes from a supplier meeting
  documents/budget.csv          Q4 ingredient budget
  documents/report.txt          Described by the client as "the monthly report"
  images/storefront.png         Photo for the website
  logs/auth.log                 Login log exported from the shop computer
  transfer/sender_hashes.sha256 SHA-256 hashes the client computed BEFORE copying

All content is synthetic and created for teaching.
"""

MEETING_NOTES = """\
Supplier meeting — 2026-09-22
Attendees: M. Alvarez, J. Okafor (Bayside Flour Co., fictional)

- Flour price rises 6% from November.
- Delivery window moves to Tuesdays 06:00–08:00.
- J. Okafor to e-mail a revised contract to orders@harborpoint.example.
- Reminder: change the shop Wi-Fi password (still the default!).
"""

BUDGET_SENT = """\
item,unit,quantity,unit_cost_usd,total_usd
bread flour,25kg bag,40,31.50,1260.00
butter,1kg block,120,7.80,936.00
sugar,10kg bag,30,9.20,276.00
yeast,500g pack,24,6.10,146.40
eggs,crate of 180,15,48.00,720.00
"""

# The received copy differs from what the client hashed: one quantity changed.
BUDGET_RECEIVED = BUDGET_SENT.replace("butter,1kg block,120,", "butter,1kg block,210,")

REPORT_INNER = """\
Monthly report — September 2026
Sales up 4% on August. Wedding-cake orders: 7.
Action: renew domain harborpoint.example before 2026-11-01.
"""

ATTACKER_IP = "203.0.113.77"   # RFC 5737 TEST-NET-3
OWNER_IP = "192.168.1.20"      # shop LAN


def _auth_log() -> str:
    lines = [
        f"Sep 29 07:58:02 shop-pc sshd[1201]: Accepted password for malvarez from {OWNER_IP} port 51022 ssh2",
        "Sep 29 07:58:02 shop-pc sshd[1201]: pam_unix(sshd:session): session opened for user malvarez",
        "Sep 29 12:10:44 shop-pc sudo:  malvarez : TTY=pts/0 ; PWD=/home/malvarez ; USER=root ; "
        "COMMAND=/usr/bin/apt update",
    ]
    users = ["admin", "root", "malvarez", "bakery", "admin", "root", "test", "malvarez", "admin", "malvarez", "root",
             "user", "malvarez", "admin"]
    second = 3
    for index, user in enumerate(users):
        pid = 2300 + index
        minute, sec = divmod(second, 60)
        stamp = f"Sep 29 23:{14 + minute:02d}:{sec:02d}"
        if user in ("malvarez",):
            lines.append(f"{stamp} shop-pc sshd[{pid}]: Failed password for {user} from {ATTACKER_IP} port "
                         f"{40112 + index * 7} ssh2")
        else:
            lines.append(f"{stamp} shop-pc sshd[{pid}]: Failed password for invalid user {user} from {ATTACKER_IP} "
                         f"port {40112 + index * 7} ssh2")
        second += 4 + (index % 3)
    lines += [
        f"Sep 29 23:15:31 shop-pc sshd[2399]: Disconnecting invalid user admin {ATTACKER_IP} port 40210: "
        "Too many authentication failures [preauth]",
        f"Sep 30 08:02:17 shop-pc sshd[2510]: Accepted password for malvarez from {OWNER_IP} port 51388 ssh2",
        "Sep 30 08:02:17 shop-pc sshd[2510]: pam_unix(sshd:session): session opened for user malvarez",
    ]
    return "\n".join(lines) + "\n"


def _png(width: int = 64, height: int = 40) -> bytes:
    """A tiny, valid RGB PNG (a striped 'awning') built without third-party libraries."""
    rows = []
    for y in range(height):
        row = bytearray([0])  # filter type 0
        for x in range(width):
            if y < 14:
                row += bytes((200, 30, 40)) if (x // 8) % 2 == 0 else bytes((245, 245, 240))
            else:
                row += bytes((150, 110, 70))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def _zip_disguised() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("monthly-report-2026-09.txt", date_time=FIXED_ZIP_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        info.create_system = 3  # Unix, fixed so output is platform-independent
        archive.writestr(info, REPORT_INNER)
    return buffer.getvalue()


def build(out: Path) -> None:
    files: dict[str, bytes] = {
        "CASE-BRIEF.txt": CASE_BRIEF.encode(),
        "documents/meeting-notes.txt": MEETING_NOTES.encode(),
        "documents/budget.csv": BUDGET_RECEIVED.encode(),
        "documents/report.txt": _zip_disguised(),
        "images/storefront.png": _png(),
        "logs/auth.log": _auth_log().encode(),
    }
    # What the client hashed before copying: identical except budget.csv (the original).
    sender_view = dict(files)
    sender_view["documents/budget.csv"] = BUDGET_SENT.encode()
    sender_lines = [
        f"{hashlib.sha256(data).hexdigest()}  {path}"
        for path, data in sorted(sender_view.items())
        if path.startswith(("documents/", "images/", "logs/"))
    ]
    files["transfer/sender_hashes.sha256"] = ("\n".join(sender_lines) + "\n").encode()

    for rel, data in files.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    write_manifest(out)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    out = Path(argv[1])
    if out.exists() and any(out.iterdir()):
        print(f"refusing to write into non-empty directory {out}", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    build(out)
    print(f"Lab 0 evidence written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
