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


def _fake_net(tmp_path, interfaces, default_route, flags=None):
    """interfaces: names; flags: optional {name: hex flags}; default UP (0x1003)."""
    net = tmp_path / "net"
    net.mkdir()
    for name in interfaces:
        (net / name).mkdir()
        (net / name / "flags").write_text((flags or {}).get(name, "0x1003") + "\n")
    route = tmp_path / "route"
    header = "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
    body = "eth0\t00000000\t010011AC\t0003\t0\t0\t0\t00000000\t0\t0\t0\n" if default_route else ""
    route.write_text(header + body)
    return net, route


def test_network_none_pass(tmp_path):
    net, route = _fake_net(tmp_path, ["lo"], default_route=False)
    assert verify.check_network("none", net, route, None).status == verify.PASS


def test_network_none_fail_with_eth0(tmp_path):
    net, route = _fake_net(tmp_path, ["lo", "eth0"], default_route=True)
    assert verify.check_network("none", net, route, None).status == verify.FAIL


def test_network_none_fail_with_up_interface_even_without_route(tmp_path):
    net, route = _fake_net(tmp_path, ["lo", "eth0"], default_route=False)
    assert verify.check_network("none", net, route, None).status == verify.FAIL


def test_network_none_ignores_docker_desktop_fallback_devices(tmp_path):
    """Regression (macOS Docker Desktop, 2026-10-09): LinuxKit exposes DOWN tunnel stubs."""
    stubs = ["erspan0", "gre0", "gretap0", "ip6_vti0", "ip6gre0", "ip6tnl0", "ip_vti0", "sit0", "tunl0"]
    net, route = _fake_net(tmp_path, ["lo", *stubs], default_route=False, flags={s: "0x80" for s in stubs})
    (net / "bonding_masters").write_text("\n")  # a file, not an interface
    result = verify.check_network("none", net, route, None)
    assert result.status == verify.PASS, result.detail


def test_ipv6_default_route_detected(tmp_path):
    net, route = _fake_net(tmp_path, ["lo"], default_route=False)
    v6 = tmp_path / "ipv6_route"
    v6.write_text("00000000000000000000000000000000 00 00000000000000000000000000000000 00 "
                  "fe800000000000000000000000000001 00000400 00000001 00000000 00000003 eth0\n")
    assert verify.check_network("none", net, route, v6).status == verify.FAIL


def test_network_internal_warns_on_default_route(tmp_path):
    net, route = _fake_net(tmp_path, ["lo", "eth0"], default_route=True)
    assert verify.check_network("internal", net, route, None).status == verify.WARN
    (tmp_path / "b").mkdir()
    net2, route2 = _fake_net(tmp_path / "b", ["lo", "eth0"], default_route=False)
    assert verify.check_network("internal", net2, route2, None).status == verify.PASS


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


# --- Pattern B checks (Lab 3) ------------------------------------------------
import http.server  # noqa: E402
import threading  # noqa: E402

from cyberlab_common.verify import check_authorization, check_http, check_no_egress  # noqa: E402


def _serve(status):
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(status)
            self.end_headers()

        def log_message(self, *a):
            pass
    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_http_check_pass_and_wrong_status():
    srv = _serve(200)
    url = f"http://127.0.0.1:{srv.server_port}/healthz"
    assert check_http([{"name": "site", "url": url}])[0].status == "PASS"
    assert check_http([{"name": "site", "url": url, "expect": 404}])[0].status == "FAIL"
    srv.shutdown()


def test_http_check_unreachable():
    res = check_http([{"url": "http://127.0.0.1:9/"}], timeout=0.5)[0]
    assert res.status == "FAIL" and "unreachable" in res.detail


def test_no_egress_pass_when_closed_and_fail_when_open():
    assert check_no_egress(["127.0.0.1:9"], timeout=0.5).status == "PASS"
    srv = _serve(200)
    assert check_no_egress([f"127.0.0.1:{srv.server_port}"]).status == "FAIL"
    srv.shutdown()


def test_authorization(tmp_path):
    f = tmp_path / "authorized-use.md"
    assert check_authorization(f, "I AGREE").status == "FAIL"
    f.write_text("Name:\nI agree\n")
    assert check_authorization(f, "I AGREE").status == "FAIL"           # no name
    f.write_text("Name: Sam Student\nI AGREE to the terms above\n")
    assert check_authorization(f, "I AGREE").status == "PASS"


def test_http_check_rejects_non_http_scheme():
    assert check_http([{"url": "file:///etc/passwd"}])[0].status == "FAIL"
