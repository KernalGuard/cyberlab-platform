import json
import os
import stat

import pytest

from cyberlab_common import manifest, verify


def test_tools_check():
    assert verify.check_tools(["sh"]).status == verify.PASS
    result = verify.check_tools(["sh", "definitely-not-a-real-tool-xyz"])
    assert result.status == verify.FAIL and "definitely-not-a-real-tool-xyz" in result.detail


def test_manifest_check_pass_and_fail(tmp_path):
    (tmp_path / "f").write_text("data")
    manifest.write_manifest(tmp_path)
    assert verify.check_manifest(tmp_path, manifest.DEFAULT_NAME).status == verify.PASS
    (tmp_path / "f").write_text("tampered")
    failed = verify.check_manifest(tmp_path, manifest.DEFAULT_NAME)
    assert failed.status == verify.FAIL and "modified: f" in failed.detail


def test_manifest_check_missing_manifest(tmp_path):
    assert verify.check_manifest(tmp_path, "MANIFEST.sha256").status == verify.FAIL


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores directory permissions")
def test_readonly_check_on_unwritable_dir(tmp_path):
    tmp_path.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        assert verify.check_readonly(tmp_path).status == verify.PASS
    finally:
        tmp_path.chmod(stat.S_IRWXU)


def test_readonly_check_fails_on_writable_dir(tmp_path):
    result = verify.check_readonly(tmp_path)
    assert result.status == verify.FAIL
    assert not any(p.name.startswith(".cyberlab-probe-") for p in tmp_path.iterdir()), "probe file left behind"


def test_writable_check(tmp_path):
    assert verify.check_writable(tmp_path).status == verify.PASS
    assert verify.check_writable(tmp_path / "nope").status == verify.FAIL


def _fake_net(tmp_path, interfaces, default_route):
    net = tmp_path / "net"
    net.mkdir()
    for name in interfaces:
        (net / name).mkdir()
    route = tmp_path / "route"
    header = "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
    body = "eth0\t00000000\t010011AC\t0003\t0\t0\t0\t00000000\t0\t0\t0\n" if default_route else ""
    route.write_text(header + body)
    return net, route


def test_network_none_pass(tmp_path):
    net, route = _fake_net(tmp_path, ["lo"], default_route=False)
    assert verify.check_network("none", net, route).status == verify.PASS


def test_network_none_fail_with_eth0(tmp_path):
    net, route = _fake_net(tmp_path, ["lo", "eth0"], default_route=True)
    assert verify.check_network("none", net, route).status == verify.FAIL


def test_network_internal_warns_on_default_route(tmp_path):
    net, route = _fake_net(tmp_path, ["lo", "eth0"], default_route=True)
    assert verify.check_network("internal", net, route).status == verify.WARN
    (tmp_path / "b").mkdir()
    net2, route2 = _fake_net(tmp_path / "b", ["lo", "eth0"], default_route=False)
    assert verify.check_network("internal", net2, route2).status == verify.PASS


def test_hardening_parses_proc_status(tmp_path):
    status = tmp_path / "status"
    status.write_text("Name:\tpython3\nCapEff:\t0000000000000000\nNoNewPrivs:\t1\n")
    results = {c.name: c.status for c in verify.check_hardening(status)}
    assert results["capabilities"] == verify.PASS
    assert results["no-new-privileges"] == verify.PASS


def test_hardening_flags_capabilities(tmp_path):
    status = tmp_path / "status"
    status.write_text("CapEff:\t00000000a80425fb\nNoNewPrivs:\t0\n")
    results = {c.name: c.status for c in verify.check_hardening(status)}
    assert results["capabilities"] == verify.FAIL
    assert results["no-new-privileges"] == verify.FAIL


@pytest.mark.parametrize("kb,expected", [(1_000_000, "FAIL"), (3_000_000, "WARN"), (8_000_000, "PASS")])
def test_memory_thresholds(tmp_path, kb, expected):
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(f"MemTotal:       {kb} kB\nMemFree:  1 kB\n")
    assert verify.check_memory({"fail": 2048, "warn": 3500}, meminfo).status == expected


def test_overall_takes_worst():
    c = verify.Check
    assert verify.overall([c("a", "PASS", ""), c("b", "WARN", "")]) == "WARN"
    assert verify.overall([c("a", "PASS", ""), c("b", "FAIL", ""), c("c", "WARN", "")]) == "FAIL"
    assert verify.overall([]) == "PASS"


def test_main_writes_report_and_exit_code(tmp_path, capsys):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "f").write_text("data")
    manifest.write_manifest(evidence)
    work = tmp_path / "work"
    work.mkdir()
    config = tmp_path / "lab.yaml"
    config.write_text(
        "id: test-lab\nversion: 0.0.1\n"
        f"evidence_dir: {evidence}\nwork_dir: {work}\nreport: {work / 'check.json'}\n"
        "checks:\n  tools: [sh]\n  manifest: MANIFEST.sha256\n"
        f"  writable: [{work}]\n"
    )
    assert verify.main(["--config", str(config)]) == 0
    report = json.loads((work / "check.json").read_text())
    assert report["overall"] == "PASS" and report["lab"] == "test-lab"
    assert "hostname" not in json.dumps(report).lower()

    (evidence / "f").write_text("tampered")
    assert verify.main(["--config", str(config)]) == 1
    assert "OVERALL: FAIL" in capsys.readouterr().out


def test_bad_config_returns_2(tmp_path):
    config = tmp_path / "lab.yaml"
    config.write_text("- just\n- a list\n")
    assert verify.main(["--config", str(config)]) == 2
