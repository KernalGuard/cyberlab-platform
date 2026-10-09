"""Environment self-check used by every lab's ``verify`` service.

A lab declares its checks in ``lab.yaml``::

    id: lab0-orientation
    version: 0.1.0
    pattern: A                      # A = offline workstation, B = internal service network
    evidence_dir: /evidence
    work_dir: /work
    report: /work/lab0-check.json   # optional machine-readable report
    checks:
      tools: [bash, sha256sum, file]
      manifest: MANIFEST.sha256     # verified inside evidence_dir
      readonly: [/evidence]
      writable: [/work]
      network: none                 # none | internal | any
      hardening: true               # non-root, no capabilities, no_new_privs
      min_memory_mb: {fail: 2048, warn: 3500}
      min_free_disk_mb: {fail: 500, warn: 2000}

Each check returns PASS, WARN or FAIL with a short, student-readable explanation.
The process exits 0 when there is no FAIL, otherwise 1. Checks never send network
traffic; isolation is inferred from interfaces and the routing table.

Command line::

    python3 -m cyberlab_common.verify --config /lab/lab.yaml [--report PATH] [--json]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import errno
import json
import os
import platform
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from . import __version__
from .manifest import verify_manifest

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
_ORDER = {PASS: 0, WARN: 1, FAIL: 2}


@dataclass
class Check:
    name: str
    status: str
    detail: str
    hint: str = ""


# --------------------------------------------------------------------------- checks


def check_tools(tools: list[str]) -> Check:
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        return Check("tools", FAIL, f"missing: {', '.join(missing)}",
                     "The image is incomplete. Pull it again: docker compose pull")
    return Check("tools", PASS, f"{len(tools)} required tools found")


def check_manifest(evidence_dir: Path, manifest_name: str) -> Check:
    try:
        result = verify_manifest(evidence_dir, manifest_name)
    except FileNotFoundError:
        return Check("evidence-integrity", FAIL, f"{manifest_name} not found in {evidence_dir}",
                     "Is the evidence folder next to compose.yaml? Re-download the evidence bundle.")
    except ValueError as exc:
        return Check("evidence-integrity", FAIL, str(exc), "The manifest is corrupted. Re-download the bundle.")
    if result.passed:
        return Check("evidence-integrity", PASS, f"all {len(result.ok)} files match {manifest_name}")
    problems = (
        [f"modified: {p}" for p in result.modified]
        + [f"missing: {p}" for p in result.missing]
        + [f"unexpected: {p}" for p in result.unexpected]
    )
    shown = "; ".join(problems[:5]) + (" ..." if len(problems) > 5 else "")
    return Check("evidence-integrity", FAIL, shown,
                 "Evidence no longer matches its manifest. Do not analyze it; re-download the bundle "
                 "and record the discrepancy in your chain-of-custody notes.")


def _probe_write(directory: Path) -> tuple[bool, int | None]:
    """Try to create and remove a file. Returns (writable, errno)."""
    try:
        fd, name = tempfile.mkstemp(prefix=".cyberlab-probe-", dir=directory)
    except OSError as exc:
        return False, exc.errno
    os.close(fd)
    try:
        os.unlink(name)
    except OSError:
        pass
    return True, None


def check_readonly(path: Path) -> Check:
    name = f"read-only:{path}"
    if not path.exists():
        return Check(name, FAIL, "path does not exist", "Check the volume mounts in compose.yaml.")
    writable, err = _probe_write(path)
    if writable:
        return Check(name, FAIL, "evidence is WRITABLE",
                     "Evidence must be mounted with ':ro'. Do not edit compose.yaml.")
    reason = errno.errorcode.get(err or 0, str(err))
    return Check(name, PASS, f"write attempt refused ({reason})")


def check_writable(path: Path) -> Check:
    name = f"writable:{path}"
    if not path.exists():
        return Check(name, FAIL, "path does not exist", "Check the volume mounts in compose.yaml.")
    writable, err = _probe_write(path)
    if writable:
        return Check(name, PASS, "work folder is writable")
    return Check(name, FAIL, f"cannot write ({errno.errorcode.get(err or 0, err)})",
                 "On Linux hosts, make the work folder writable by UID 1000: sudo chown -R 1000:1000 work")


def _interfaces(sys_class_net: Path) -> list[str]:
    try:
        return sorted(p.name for p in sys_class_net.iterdir())
    except OSError:
        return []


def _has_default_route(proc_net_route: Path) -> bool:
    try:
        lines = proc_net_route.read_text().splitlines()[1:]
    except OSError:
        return False
    return any(len(cols) > 1 and cols[1] == "00000000" for cols in (line.split() for line in lines))


def check_network(mode: str, sys_class_net: Path = Path("/sys/class/net"),
                  proc_net_route: Path = Path("/proc/net/route")) -> Check:
    interfaces = _interfaces(sys_class_net)
    default_route = _has_default_route(proc_net_route)
    if mode == "none":
        extra = [i for i in interfaces if i != "lo"]
        if extra or default_route:
            return Check("network-isolation", FAIL, f"unexpected interfaces {extra or '[]'}; "
                         f"default route={'yes' if default_route else 'no'}",
                         "This lab must run with network_mode: none. Use the lab's compose.yaml unmodified.")
        return Check("network-isolation", PASS, "no network: loopback only")
    if mode == "internal":
        if default_route:
            return Check("network-isolation", WARN, "a default route exists",
                         "Expected an internal-only network. Confirm 'internal: true' in compose.yaml.")
        return Check("network-isolation", PASS, f"internal network only ({', '.join(interfaces)})")
    return Check("network-isolation", PASS, f"network not restricted by design ({mode})")


def _status_fields(proc_self_status: Path) -> dict[str, str]:
    fields = {}
    try:
        for line in proc_self_status.read_text().splitlines():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    except OSError:
        pass
    return fields


def check_hardening(proc_self_status: Path = Path("/proc/self/status")) -> list[Check]:
    fields = _status_fields(proc_self_status)
    checks = []
    uid = os.geteuid()
    checks.append(Check("non-root", PASS if uid != 0 else FAIL, f"running as UID {uid}",
                        "" if uid != 0 else "Containers must run as the 'analyst' user (UID 1000)."))
    cap_eff = fields.get("CapEff")
    if cap_eff is None:
        checks.append(Check("capabilities", WARN, "could not read CapEff"))
    else:
        dropped = int(cap_eff, 16) == 0
        checks.append(Check("capabilities", PASS if dropped else FAIL,
                            "all capabilities dropped" if dropped else f"effective capabilities present: 0x{cap_eff}",
                            "" if dropped else "Expected cap_drop: [ALL]."))
    nnp = fields.get("NoNewPrivs")
    if nnp is None:
        checks.append(Check("no-new-privileges", WARN, "could not read NoNewPrivs"))
    else:
        checks.append(Check("no-new-privileges", PASS if nnp == "1" else FAIL,
                            f"NoNewPrivs={nnp}",
                            "" if nnp == "1" else "Expected security_opt: no-new-privileges:true."))
    return checks


def _mem_total_mb(proc_meminfo: Path) -> int | None:
    try:
        for line in proc_meminfo.read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def check_memory(thresholds: dict, proc_meminfo: Path = Path("/proc/meminfo")) -> Check:
    total = _mem_total_mb(proc_meminfo)
    if total is None:
        return Check("docker-memory", WARN, "could not read /proc/meminfo")
    hint = ("Docker has too little memory. Docker Desktop (macOS): Settings → Resources → Memory, set 4 GB. "
            "Windows (WSL 2): set 'memory=4GB' under [wsl2] in %UserProfile%\\.wslconfig, then 'wsl --shutdown'.")
    if total < thresholds.get("fail", 0):
        return Check("docker-memory", FAIL, f"{total} MB available to Docker", hint)
    if total < thresholds.get("warn", 0):
        detail = f"{total} MB available to Docker (recommended ≥ {thresholds['warn']} MB)"
        return Check("docker-memory", WARN, detail, hint)
    return Check("docker-memory", PASS, f"{total} MB available to Docker")


def check_disk(path: Path, thresholds: dict) -> Check:
    try:
        free_mb = shutil.disk_usage(path).free // (1024 * 1024)
    except OSError as exc:
        return Check("free-disk", WARN, f"could not measure: {exc}")
    hint = "Free disk space, or remove unused images: docker system df, then docker image prune"
    if free_mb < thresholds.get("fail", 0):
        return Check("free-disk", FAIL, f"{free_mb} MB free", hint)
    if free_mb < thresholds.get("warn", 0):
        return Check("free-disk", WARN, f"{free_mb} MB free (recommended ≥ {thresholds['warn']} MB)", hint)
    return Check("free-disk", PASS, f"{free_mb} MB free")


# ------------------------------------------------------------------------- runner


def environment_info() -> dict:
    """Non-identifying facts about the runtime (no hostnames, usernames or IPs)."""
    return {
        "architecture": platform.machine(),
        "kernel": platform.release(),
        "cpus_visible": os.cpu_count(),
        "memory_mb": _mem_total_mb(Path("/proc/meminfo")),
        "python": platform.python_version(),
        "cyberlab_common": __version__,
        "image_version": os.environ.get("CYBERLAB_IMAGE_VERSION", "unknown"),
    }


def run_checks(config: dict) -> list[Check]:
    checks_cfg = config.get("checks", {}) or {}
    evidence_dir = Path(config.get("evidence_dir", "/evidence"))
    work_dir = Path(config.get("work_dir", "/work"))
    results: list[Check] = []

    if "tools" in checks_cfg:
        results.append(check_tools(list(checks_cfg["tools"])))
    if "manifest" in checks_cfg:
        results.append(check_manifest(evidence_dir, checks_cfg["manifest"]))
    for path in checks_cfg.get("readonly", []) or []:
        results.append(check_readonly(Path(path)))
    for path in checks_cfg.get("writable", []) or []:
        results.append(check_writable(Path(path)))
    if "network" in checks_cfg:
        results.append(check_network(checks_cfg["network"]))
    if checks_cfg.get("hardening"):
        results.extend(check_hardening())
    if "min_memory_mb" in checks_cfg:
        results.append(check_memory(checks_cfg["min_memory_mb"]))
    if "min_free_disk_mb" in checks_cfg:
        results.append(check_disk(work_dir, checks_cfg["min_free_disk_mb"]))
    return results


def overall(results: list[Check]) -> str:
    return max((r.status for r in results), key=_ORDER.__getitem__, default=PASS)


def build_report(config: dict, results: list[Check]) -> dict:
    return {
        "schema": "cyberlab-verify-report/1",
        "lab": config.get("id", "unknown"),
        "lab_version": str(config.get("version", "unknown")),
        "generated_utc": _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat(),
        "environment": environment_info(),
        "overall": overall(results),
        "checks": [asdict(r) for r in results],
    }


def format_table(results: list[Check]) -> str:
    width = max((len(r.name) for r in results), default=10)
    lines = []
    for r in results:
        lines.append(f"[{r.status}] {r.name.ljust(width)}  {r.detail}")
        if r.hint and r.status != PASS:
            lines.append(f"       {''.ljust(width)}  → {r.hint}")
    return "\n".join(lines)


def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at top level")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cyberlab-verify", description="Check that this lab environment is ready.")
    parser.add_argument("--config", type=Path, default=Path("/lab/lab.yaml"))
    parser.add_argument("--report", type=Path, help="write a JSON report here (overrides lab.yaml)")
    parser.add_argument("--json", action="store_true", help="print the JSON report instead of a table")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"[FAIL] cannot read lab configuration: {exc}", file=sys.stderr)
        return 2

    results = run_checks(config)
    report = build_report(config, results)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"CyberLab verify — {report['lab']} v{report['lab_version']} "
              f"({report['environment']['architecture']})")
        print(format_table(results))
        print(f"\nOVERALL: {report['overall']}")

    report_path = args.report or (Path(config["report"]) if config.get("report") else None)
    if report_path:
        try:
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            if not args.json:
                print(f"Report saved to {report_path}")
        except OSError as exc:
            print(f"[WARN] could not save report to {report_path}: {exc}", file=sys.stderr)

    return 1 if report["overall"] == FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
