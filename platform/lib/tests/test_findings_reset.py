import datetime as dt
import json

import pytest

from cyberlab_common import findings, reset

KEY = {
    "schema": "cyberlab-answer-key/1",
    "lab": "lab1-network-traffic",
    "variant": "K7QX-2M4P",
    "items": {
        "host": {"answer": "10.20.30.44", "points": 5, "match": "exact"},
        "domains": {"answer": ["a.example", "b.example"], "points": 6, "match": "set"},
        "first": {"answer": "2026-10-03T14:15:02Z", "points": 4, "match": "timestamp", "tolerance_s": 1},
        "count": {"answer": 12, "points": 2, "match": "number"},
        "proto": {"answer": "HTTP", "points": 3, "match": "casefold"},
    },
}


def submission(items, variant="K7QX-2M4P"):
    return {"schema": "cyberlab-findings/1", "lab": "lab1-network-traffic", "variant": variant, "items": items}


def test_perfect_submission_scores_full():
    sub = submission({"host": "10.20.30.44", "domains": ["B.example", "a.example"],
                      "first": "2026-10-03 14:15:03+00:00", "count": 12, "proto": "http"})
    report = findings.score(sub, KEY)
    assert report["points_awarded"] == report["points_possible"] == 20
    assert report["flags"] == []


def test_blank_submission_scores_zero():
    report = findings.score(submission({}), KEY)
    assert report["points_awarded"] == 0
    assert {i["status"] for i in report["items"]} == {"missing"}


def test_set_partial_credit_penalises_extras():
    item = findings.score_item("domains", KEY["items"]["domains"], ["a.example", "wrong.example"])
    assert item.points_awarded == 0 and item.status == "incorrect"
    item = findings.score_item("domains", KEY["items"]["domains"], ["a.example"])
    assert item.points_awarded == 3 and item.status == "partial"


def test_timestamp_tolerance_and_naive_is_utc():
    spec = KEY["items"]["first"]
    assert findings.score_item("first", spec, "2026-10-03T14:15:02").status == "correct"
    assert findings.score_item("first", spec, "2026-10-03T14:15:05Z").status == "incorrect"
    assert findings.score_item("first", spec, "not a time").status == "incorrect"


def test_variant_mismatch_is_flagged():
    report = findings.score(submission({"host": "10.20.30.44"}, variant="ZZZZ-ZZZZ"), KEY)
    assert any("variant mismatch" in f for f in report["flags"])


@pytest.mark.parametrize("bad", [
    [],
    {"schema": "wrong", "lab": "x", "variant": "y", "items": {}},
    {"schema": "cyberlab-findings/1", "lab": "", "variant": "y", "items": {}},
    {"schema": "cyberlab-findings/1", "lab": "x", "variant": "y", "items": []},
    {"schema": "cyberlab-findings/1", "lab": "x", "variant": "y", "items": {"a": {"nested": 1}}},
    {"schema": "cyberlab-findings/1", "lab": "x", "variant": "y", "items": {"a": True}},
])
def test_invalid_findings_rejected(bad):
    with pytest.raises(findings.FindingsError):
        findings.validate_findings(bad)


def test_unknown_match_rule_raises():
    with pytest.raises(ValueError):
        findings.score_item("x", {"answer": 1, "points": 1, "match": "regex"}, 1)


def test_cli_validate(tmp_path, capsys):
    path = tmp_path / "findings.json"
    path.write_text(json.dumps(submission({"host": "1.2.3.4"})))
    assert findings.main(["validate", str(path)]) == 0
    path.write_text("{not json")
    assert findings.main(["validate", str(path)]) == 1


def test_reset_backs_up_and_restores(tmp_path):
    template = tmp_path / "template"
    template.mkdir()
    (template / "notes.md").write_text("# Notes\n")
    (template / "sub").mkdir()
    (template / "sub" / "x.txt").write_text("x")
    work = tmp_path / "work"
    work.mkdir()
    (work / "notes.md").write_text("my precious notes")
    (work / "extra.txt").write_text("extra")

    backup = reset.reset_work(template, work, now=dt.datetime(2026, 10, 9, 12, 0, tzinfo=dt.UTC))
    assert (work / "notes.md").read_text() == "# Notes\n"
    assert (work / "sub" / "x.txt").exists()
    assert not (work / "extra.txt").exists()
    assert backup == work / ".backup" / "20261009T120000Z"
    assert (backup / "notes.md").read_text() == "my precious notes"


def test_reset_on_empty_work_makes_no_backup(tmp_path):
    template = tmp_path / "t"
    template.mkdir()
    (template / "a").write_text("a")
    assert reset.reset_work(template, tmp_path / "w") is None
    assert (tmp_path / "w" / "a").exists()


def test_reset_missing_template(tmp_path):
    with pytest.raises(FileNotFoundError):
        reset.reset_work(tmp_path / "missing", tmp_path / "w")
