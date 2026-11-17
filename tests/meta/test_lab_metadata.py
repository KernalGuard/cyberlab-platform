"""Every lab's lab.yaml parses and has the keys verify and the policy tests rely on (no Docker needed)."""

from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
LAB_FILES = sorted((REPO / "labs").glob("*/lab.yaml"))
REQUIRED = {"id", "title", "version", "pattern", "evidence_dir", "work_dir", "report", "checks"}


def test_labs_found():
    assert LAB_FILES


@pytest.mark.parametrize("path", LAB_FILES, ids=[p.parent.name for p in LAB_FILES])
def test_lab_yaml_valid(path):
    meta = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(meta, dict), "lab.yaml must be a mapping"
    missing = REQUIRED - meta.keys()
    assert not missing, f"missing keys: {sorted(missing)}"
    assert meta["id"] == path.parent.name
    assert meta["pattern"] in ("A", "B")
    for obj in meta.get("objectives", []):
        assert {"id", "bloom", "text"} <= obj.keys()
