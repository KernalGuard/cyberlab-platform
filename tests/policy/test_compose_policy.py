"""Security policy tests on the *resolved* Compose configuration of every lab.

Runs `docker compose config --format json` (needs the Docker CLI with Compose v2,
but no daemon access to registries) and asserts SEC-01 … SEC-07 for every service.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
LABS = sorted(p.parent for p in (REPO / "labs").glob("*/compose.yaml"))

pytestmark = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI not installed")


def resolved(lab: Path) -> dict:
    proc = subprocess.run(["docker", "compose", "config", "--format", "json"], cwd=lab,
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def lab_meta(lab: Path) -> dict:
    return yaml.safe_load((lab / "lab.yaml").read_text())


def services():
    for lab in LABS:
        config = resolved(lab)
        for name, svc in config["services"].items():
            yield pytest.param(lab, name, svc, id=f"{lab.name}:{name}")


@pytest.mark.parametrize("lab,name,svc", list(services()))
class TestServicePolicy:
    def test_not_privileged(self, lab, name, svc):
        assert not svc.get("privileged", False)

    def test_no_host_namespaces(self, lab, name, svc):
        assert svc.get("network_mode") != "host"
        assert svc.get("pid") != "host"
        assert svc.get("ipc") != "host"

    def test_no_docker_socket_or_sensitive_mounts(self, lab, name, svc):
        for vol in svc.get("volumes", []):
            source = str(vol.get("source", ""))
            assert "docker.sock" not in source
            assert source not in ("/", "/etc", "/var", "/root", str(Path.home()))

    def test_non_root_user(self, lab, name, svc):
        user = str(svc.get("user", ""))
        assert user and user.split(":")[0] not in ("0", "root"), "service must set a non-root user"

    def test_capabilities_dropped(self, lab, name, svc):
        assert "ALL" in svc.get("cap_drop", [])
        assert not svc.get("cap_add"), "cap_add requires an ADR exception"

    def test_no_new_privileges(self, lab, name, svc):
        assert any(opt.replace("=", ":") in ("no-new-privileges:true", "no-new-privileges")
                   for opt in svc.get("security_opt", []))

    def test_read_only_rootfs(self, lab, name, svc):
        assert svc.get("read_only") is True

    def test_resource_limits(self, lab, name, svc):
        assert svc.get("mem_limit"), "mem_limit required"
        assert svc.get("pids_limit"), "pids_limit required"
        assert svc.get("cpus"), "cpus required"

    def test_network_pattern(self, lab, name, svc):
        pattern = lab_meta(lab).get("pattern")
        if pattern == "A":
            assert svc.get("network_mode") == "none", "Pattern A labs must have no network"
            assert not svc.get("ports"), "Pattern A labs publish no ports"

    def test_ports_loopback_only(self, lab, name, svc):
        for port in svc.get("ports", []):
            assert port.get("host_ip") == "127.0.0.1", f"port {port} must bind to 127.0.0.1"

    def test_evidence_mounted_read_only(self, lab, name, svc):
        for vol in svc.get("volumes", []):
            if vol.get("target") == "/evidence":
                assert vol.get("read_only") is True


def test_every_lab_found():
    assert LABS, "no labs discovered"


@pytest.mark.parametrize("lab", LABS, ids=[lab.name for lab in LABS])
def test_internal_networks_for_pattern_b(lab):
    if lab_meta(lab).get("pattern") != "B":
        pytest.skip("not a Pattern B lab")
    networks = resolved(lab).get("networks", {})
    internal = [n for n, cfg in networks.items() if cfg.get("internal")]
    assert internal, "Pattern B labs need at least one internal: true network"
