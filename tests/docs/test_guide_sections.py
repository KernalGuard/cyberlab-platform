"""FR-I-01: every lab's student guide contains the 16 required sections, in order."""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GUIDES = sorted((REPO / "labs").glob("*/docs/student-guide.md"))

REQUIRED = [
    "laboratory title", "course level", "estimated completion time", "prerequisite knowledge",
    "learning objectives", "scenario background", "environment requirements", "setup instructions",
    "investigation tasks", "guided questions", "independent challenge", "required deliverables",
    "submission instructions", "troubleshooting", "cleanup instructions", "reflection questions",
]


def test_guides_exist():
    assert GUIDES


@pytest.mark.parametrize("guide", GUIDES, ids=[g.parts[-3] for g in GUIDES])
def test_sixteen_sections_in_order(guide):
    headings = re.findall(r"^## (\d+)\. (.+)$", guide.read_text(), re.M)
    titles = [re.sub(r"\s*\(.*\)$", "", title).strip().lower() for _, title in headings]  # allow "(optional)"
    assert [int(n) for n, _ in headings] == list(range(1, 17)), headings
    assert titles == REQUIRED


@pytest.mark.parametrize("guide", GUIDES, ids=[g.parts[-3] for g in GUIDES])
def test_objectives_are_bloom_tagged(guide):
    text = guide.read_text()
    section = text.split("## 5. Learning objectives", 1)[1].split("## 6.", 1)[0]
    rows = [line for line in section.splitlines() if re.match(r"^\| L\d", line)]
    levels = {"Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"}
    assert len(rows) >= 5
    assert all(any(level in row for level in levels) for row in rows)


@pytest.mark.parametrize("guide", GUIDES, ids=[g.parts[-3] for g in GUIDES])
def test_guide_declares_test_status(guide):
    assert re.search(r"\*\*Status:\*\*", guide.read_text()), "guide must state its tested/untested status"
