"""Validate student ``findings.json`` files and score them against an answer key.

``findings.json`` (student-facing; schema in ``platform/schemas/findings.schema.json``)::

    {
      "schema": "cyberlab-findings/1",
      "lab": "lab1-network-traffic",
      "variant": "K7QX-2M4P",
      "items": {
        "suspicious_host_ip": "10.20.30.44",
        "c2_domains": ["a1b2c3.example", "d4e5f6.example"],
        "first_beacon_utc": "2026-10-03T14:15:02Z"
      }
    }

Answer key (instructor-only, generated per seed)::

    {
      "schema": "cyberlab-answer-key/1",
      "lab": "lab1-network-traffic",
      "variant": "K7QX-2M4P",
      "items": {
        "suspicious_host_ip": {"answer": "10.20.30.44", "points": 5, "match": "exact"},
        "c2_domains": {"answer": ["a1b2c3.example", "d4e5f6.example"], "points": 6, "match": "set"},
        "first_beacon_utc": {"answer": "2026-10-03T14:15:02Z", "points": 4,
                             "match": "timestamp", "tolerance_s": 1}
      }
    }

Match rules: ``exact``, ``casefold``, ``set`` (order-insensitive, case-insensitive,
partial credit = |correct| / |expected| minus wrong extras, floored at 0),
``number`` (``tolerance`` absolute), ``timestamp`` (ISO 8601, ``tolerance_s``).

The checker scores only objectively verifiable items. Methodology, reasoning and
communication are scored by a human with the rubric.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

FINDINGS_SCHEMA = "cyberlab-findings/1"
KEY_SCHEMA = "cyberlab-answer-key/1"
_SCALAR = (str, int, float)


class FindingsError(ValueError):
    """Raised when a findings file is structurally invalid."""


def validate_findings(data: object) -> dict:
    """Return the findings dict if structurally valid, else raise FindingsError."""
    if not isinstance(data, dict):
        raise FindingsError("findings must be a JSON object")
    if data.get("schema") != FINDINGS_SCHEMA:
        raise FindingsError(f"'schema' must be {FINDINGS_SCHEMA!r}")
    for field in ("lab", "variant"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise FindingsError(f"'{field}' must be a non-empty string")
    items = data.get("items")
    if not isinstance(items, dict):
        raise FindingsError("'items' must be an object")
    for key, value in items.items():
        ok = value is None or isinstance(value, _SCALAR) or (
            isinstance(value, list) and all(isinstance(v, _SCALAR) for v in value)
        )
        if not ok or isinstance(value, bool):
            raise FindingsError(f"item {key!r}: value must be a string, number, list of those, or null")
    return data


def _parse_ts(value: object) -> _dt.datetime | None:
    if not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:  # naive timestamps are interpreted as UTC, as the guides instruct
        parsed = parsed.replace(tzinfo=_dt.UTC)
    return parsed


def _norm(value: object) -> str:
    return str(value).strip().casefold()


@dataclass
class ItemScore:
    item: str
    points_possible: float
    points_awarded: float
    status: str  # correct | partial | incorrect | missing
    note: str = ""


def score_item(item: str, spec: dict, submitted: object) -> ItemScore:
    points = float(spec.get("points", 0))
    expected = spec.get("answer")
    rule = spec.get("match", "exact")

    if submitted is None or submitted == "" or submitted == []:
        return ItemScore(item, points, 0.0, "missing")

    if rule == "exact":
        good = str(submitted).strip() == str(expected).strip()
    elif rule == "casefold":
        good = _norm(submitted) == _norm(expected)
    elif rule == "number":
        try:
            good = abs(float(submitted) - float(expected)) <= float(spec.get("tolerance", 0))
        except (TypeError, ValueError):
            good = False
    elif rule == "timestamp":
        got, want = _parse_ts(submitted), _parse_ts(expected)
        good = bool(got and want and abs((got - want).total_seconds()) <= float(spec.get("tolerance_s", 0)))
    elif rule == "set":
        want = {_norm(v) for v in expected}
        got = {_norm(v) for v in (submitted if isinstance(submitted, list) else [submitted])}
        correct, wrong = len(got & want), len(got - want)
        fraction = max(0.0, (correct - wrong) / len(want)) if want else 0.0
        awarded = round(points * fraction, 2)
        status = "correct" if fraction == 1.0 else ("partial" if awarded > 0 else "incorrect")
        return ItemScore(item, points, awarded, status, f"{correct}/{len(want)} correct, {wrong} extra")
    else:
        raise ValueError(f"{item}: unknown match rule {rule!r}")

    return ItemScore(item, points, points if good else 0.0, "correct" if good else "incorrect")


def score(findings: dict, key: dict) -> dict:
    """Score findings against a key. Flags a variant mismatch (possible copied work)."""
    validate_findings(findings)
    if key.get("schema") != KEY_SCHEMA:
        raise ValueError(f"answer key 'schema' must be {KEY_SCHEMA!r}")
    submitted = findings["items"]
    results = [score_item(item, spec, submitted.get(item)) for item, spec in key["items"].items()]
    possible = sum(r.points_possible for r in results)
    awarded = round(sum(r.points_awarded for r in results), 2)
    flags = []
    if findings["lab"] != key.get("lab"):
        flags.append(f"lab mismatch: submitted {findings['lab']!r}, key {key.get('lab')!r}")
    if findings["variant"].strip().upper() != str(key.get("variant", "")).upper():
        flags.append(f"variant mismatch: submitted {findings['variant']!r}, key {key.get('variant')!r}")
    unknown = sorted(set(submitted) - set(key["items"]))
    if unknown:
        flags.append(f"unrecognised items ignored: {', '.join(unknown)}")
    return {
        "lab": key.get("lab"),
        "variant": key.get("variant"),
        "points_awarded": awarded,
        "points_possible": possible,
        "items": [asdict(r) for r in results],
        "flags": flags,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cyberlab-findings")
    sub = parser.add_subparsers(dest="action", required=True)
    v = sub.add_parser("validate", help="check a findings.json file is well-formed")
    v.add_argument("findings", type=Path)
    s = sub.add_parser("score", help="score findings against an answer key (instructor)")
    s.add_argument("findings", type=Path)
    s.add_argument("key", type=Path)
    args = parser.parse_args(argv)

    try:
        findings = json.loads(args.findings.read_text(encoding="utf-8"))
        if args.action == "validate":
            validate_findings(findings)
            print(f"PASS: {args.findings} is valid ({len(findings['items'])} items)")
            return 0
        report = score(findings, json.loads(args.key.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
