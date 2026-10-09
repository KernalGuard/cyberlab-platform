"""Lab 0 evidence tests: determinism, integrity of the committed copy, teaching properties."""

import hashlib
import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[1]
REPO = LAB.parents[1]
sys.path.insert(0, str(REPO / "platform" / "lib"))

from cyberlab_common.manifest import parse_manifest, verify_manifest  # noqa: E402

spec = importlib.util.spec_from_file_location("build_evidence", LAB / "scripts" / "build_evidence.py")
build_evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_evidence)

COMMITTED = LAB / "evidence"


def _tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def test_generator_is_deterministic(tmp_path):
    build_evidence.build(tmp_path / "a")
    build_evidence.build(tmp_path / "b")
    assert _tree(tmp_path / "a") == _tree(tmp_path / "b")


def test_committed_evidence_matches_generator(tmp_path):
    """Fails if someone edits evidence by hand instead of changing the generator."""
    build_evidence.build(tmp_path / "fresh")
    assert _tree(COMMITTED) == _tree(tmp_path / "fresh")


def test_committed_evidence_matches_manifest():
    assert verify_manifest(COMMITTED).passed


def test_report_is_a_disguised_zip():
    data = (COMMITTED / "documents" / "report.txt").read_bytes()
    assert data[:4] == b"PK\x03\x04"
    with zipfile.ZipFile(COMMITTED / "documents" / "report.txt") as archive:
        assert archive.namelist() == ["monthly-report-2026-09.txt"]


def test_png_magic():
    assert (COMMITTED / "images" / "storefront.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_exactly_one_sender_hash_mismatch():
    sender = parse_manifest((COMMITTED / "transfer" / "sender_hashes.sha256").read_text())
    mismatched = [rel for rel, digest in sender.items()
                  if hashlib.sha256((COMMITTED / rel).read_bytes()).hexdigest() != digest]
    assert mismatched == ["documents/budget.csv"]


def test_auth_log_answer_facts():
    """These values are the Lab 0 answer key (instructor guide, Part C)."""
    lines = (COMMITTED / "logs" / "auth.log").read_text().splitlines()
    failed = [line for line in lines if "Failed password" in line]
    assert len(failed) == 14
    assert {line.split(" from ")[1].split()[0] for line in failed} == {"203.0.113.77"}
    assert sum("for malvarez from" in line for line in failed) == 4
    assert failed[0].startswith("Sep 29 23:14:03")


def test_no_real_looking_identifiers():
    text = "\n".join(p.read_text(errors="ignore") for p in COMMITTED.rglob("*") if p.suffix in {".txt", ".log", ".csv"})
    for tld in (".com", ".org", ".net", ".edu"):
        assert tld not in text, f"real TLD {tld} found; use .example"


@pytest.mark.parametrize("cmd", [["sha256sum", "-c", "MANIFEST.sha256"]])
def test_guide_command_manifest_check(cmd):
    proc = subprocess.run(cmd, cwd=COMMITTED, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout
