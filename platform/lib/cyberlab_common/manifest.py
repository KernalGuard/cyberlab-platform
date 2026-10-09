"""Create and verify SHA-256 evidence manifests.

Manifest format (identical to GNU ``sha256sum`` output, so students can also
run ``sha256sum -c MANIFEST.sha256`` by hand)::

    <64 hex chars><two spaces><relative/path/with/forward/slashes>

Lines are sorted by path so the manifest itself is deterministic.

Command line::

    python3 -m cyberlab_common.manifest create <evidence_dir> [--name MANIFEST.sha256]
    python3 -m cyberlab_common.manifest verify <evidence_dir> [--name MANIFEST.sha256]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_NAME = "MANIFEST.sha256"
_CHUNK = 1024 * 1024


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, streaming in 1 MiB chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def _iter_files(root: Path, manifest_name: str):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            rel = path.relative_to(root).as_posix()
            if rel == manifest_name:
                continue
            yield rel, path


def build_manifest(root: Path, manifest_name: str = DEFAULT_NAME) -> str:
    """Return manifest text for every regular file under ``root``."""
    root = Path(root)
    lines = [f"{sha256_file(path)}  {rel}" for rel, path in _iter_files(root, manifest_name)]
    return "\n".join(lines) + ("\n" if lines else "")


def write_manifest(root: Path, manifest_name: str = DEFAULT_NAME) -> Path:
    root = Path(root)
    target = root / manifest_name
    target.write_text(build_manifest(root, manifest_name), encoding="utf-8", newline="\n")
    return target


def parse_manifest(text: str) -> dict[str, str]:
    """Parse manifest text into ``{relative_path: sha256}``.

    Raises ``ValueError`` on malformed lines so a corrupted manifest is never
    silently treated as "nothing to check".
    """
    entries: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\r")
        if not line.strip():
            continue
        digest, sep, rel = line.partition("  ")
        if sep != "  " or len(digest) != 64 or not all(c in "0123456789abcdef" for c in digest):
            raise ValueError(f"malformed manifest line {number}: {raw!r}")
        rel = rel.lstrip("*")  # sha256sum binary-mode marker
        if rel in entries:
            raise ValueError(f"duplicate manifest entry on line {number}: {rel}")
        entries[rel] = digest
    return entries


@dataclass
class VerifyResult:
    ok: list[str]
    modified: list[str]
    missing: list[str]
    unexpected: list[str]

    @property
    def passed(self) -> bool:
        return not (self.modified or self.missing or self.unexpected)

    def summary(self) -> str:
        return (
            f"{len(self.ok)} OK, {len(self.modified)} modified, "
            f"{len(self.missing)} missing, {len(self.unexpected)} unexpected"
        )


def verify_manifest(root: Path, manifest_name: str = DEFAULT_NAME) -> VerifyResult:
    """Compare files under ``root`` against its manifest."""
    root = Path(root)
    manifest_path = root / manifest_name
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    expected = parse_manifest(manifest_path.read_text(encoding="utf-8"))
    actual = dict(_iter_files(root, manifest_name))

    ok, modified, missing = [], [], []
    for rel, digest in sorted(expected.items()):
        path = actual.get(rel)
        if path is None:
            missing.append(rel)
        elif sha256_file(path) == digest:
            ok.append(rel)
        else:
            modified.append(rel)
    unexpected = sorted(set(actual) - set(expected))
    return VerifyResult(ok, modified, missing, unexpected)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cyberlab-manifest", description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=["create", "verify"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--name", default=DEFAULT_NAME, help="manifest filename (default: %(default)s)")
    args = parser.parse_args(argv)

    if args.action == "create":
        target = write_manifest(args.directory, args.name)
        print(f"wrote {target}")
        return 0

    try:
        result = verify_manifest(args.directory, args.name)
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    for rel in result.modified:
        print(f"MODIFIED    {rel}")
    for rel in result.missing:
        print(f"MISSING     {rel}")
    for rel in result.unexpected:
        print(f"UNEXPECTED  {rel}")
    print(("PASS: " if result.passed else "FAIL: ") + result.summary())
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
