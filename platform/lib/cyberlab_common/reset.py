"""Restore a lab's work folder from its template without destroying student work.

Existing contents of the work folder are moved into ``.backup/<UTC timestamp>/``
first, so a student who resets by mistake can recover their notes. Evidence is
never touched (it is mounted read-only).

Command line::

    python3 -m cyberlab_common.reset --template /lab/work.template --work /work
"""

from __future__ import annotations

import argparse
import datetime as _dt
import shutil
import sys
from pathlib import Path

BACKUP_DIR = ".backup"


def reset_work(template: Path, work: Path, now: _dt.datetime | None = None) -> Path | None:
    """Back up current work contents, then copy the template in. Returns the backup path."""
    if not template.is_dir():
        raise FileNotFoundError(f"template folder not found: {template}")
    work.mkdir(parents=True, exist_ok=True)
    stamp = (now or _dt.datetime.now(_dt.UTC)).strftime("%Y%m%dT%H%M%SZ")

    current = [p for p in work.iterdir() if p.name not in (BACKUP_DIR, ".gitkeep")]
    backup = None
    if current:
        backup = work / BACKUP_DIR / stamp
        backup.mkdir(parents=True, exist_ok=False)
        for item in current:
            shutil.move(str(item), backup / item.name)

    for item in template.iterdir():
        target = work / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    return backup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cyberlab-reset", description=__doc__.splitlines()[0])
    parser.add_argument("--template", type=Path, default=Path("/lab/work.template"))
    parser.add_argument("--work", type=Path, default=Path("/work"))
    args = parser.parse_args(argv)
    try:
        backup = reset_work(args.template, args.work)
    except (OSError, FileNotFoundError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if backup:
        print(f"Previous work moved to {backup}")
    print(f"PASS: {args.work} restored from template")
    return 0


if __name__ == "__main__":
    sys.exit(main())
