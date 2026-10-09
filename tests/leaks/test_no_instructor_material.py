"""SEC-09: the public repository must never contain instructor-only material."""

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Files that legitimately mention the answer-key schema (documentation and the checker itself).
ALLOWED = {
    "platform/lib/cyberlab_common/findings.py",
    "platform/lib/tests/test_findings_reset.py",
    "tests/leaks/test_no_instructor_material.py",
}
FORBIDDEN_NAME = re.compile(r"(answer[-_]?key|seed[-_]?map|roster|course[-_]?secret|pseudonym[-_]?map)", re.I)
FORBIDDEN_TEXT = ['"schema": "cyberlab-answer-key/1"', "COURSE_SECRET=", "BEGIN AGE ENCRYPTED FILE"]


def tracked_files() -> list[str]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True).stdout
        files = out.splitlines()
    except (OSError, subprocess.CalledProcessError):
        files = []
    if not files:  # not a git checkout: scan the tree
        files = [p.relative_to(REPO).as_posix() for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts]
    return files


def test_no_instructor_filenames():
    offenders = [f for f in tracked_files() if FORBIDDEN_NAME.search(Path(f).name) and f not in ALLOWED]
    assert not offenders, f"instructor-only files in public repo: {offenders}"


def test_no_answer_keys_or_secrets_in_content():
    offenders = []
    for rel in tracked_files():
        if rel in ALLOWED or rel.startswith("docs/"):
            continue
        path = REPO / rel
        try:
            text = path.read_text(errors="ignore")
        except (OSError, IsADirectoryError):
            continue
        offenders += [f"{rel}: {needle}" for needle in FORBIDDEN_TEXT if needle in text]
    assert not offenders, offenders
