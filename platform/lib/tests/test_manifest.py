import hashlib
import shutil
import subprocess

import pytest

from cyberlab_common import manifest


@pytest.fixture
def evidence(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.txt").write_bytes(b"alpha\n")
    (tmp_path / "b.bin").write_bytes(bytes(range(256)))
    (tmp_path / "docs" / "space name.txt").write_bytes(b"spaces are allowed\n")
    return tmp_path


def test_sha256_file_matches_hashlib(evidence):
    assert manifest.sha256_file(evidence / "b.bin") == hashlib.sha256(bytes(range(256))).hexdigest()


def test_sha256_large_file_streams(tmp_path):
    big = tmp_path / "big"
    big.write_bytes(b"x" * (3 * 1024 * 1024 + 17))
    assert manifest.sha256_file(big) == hashlib.sha256(b"x" * (3 * 1024 * 1024 + 17)).hexdigest()


def test_manifest_is_sorted_and_excludes_itself(evidence):
    manifest.write_manifest(evidence)
    text = (evidence / manifest.DEFAULT_NAME).read_text()
    paths = [line.split("  ", 1)[1] for line in text.splitlines()]
    assert paths == sorted(paths)
    assert manifest.DEFAULT_NAME not in paths
    assert "docs/space name.txt" in paths


def test_manifest_is_deterministic(evidence):
    assert manifest.build_manifest(evidence) == manifest.build_manifest(evidence)


def test_verify_passes_on_untouched_evidence(evidence):
    manifest.write_manifest(evidence)
    result = manifest.verify_manifest(evidence)
    assert result.passed
    assert len(result.ok) == 3


def test_verify_detects_modification(evidence):
    manifest.write_manifest(evidence)
    (evidence / "docs" / "a.txt").write_bytes(b"ALPHA\n")
    result = manifest.verify_manifest(evidence)
    assert not result.passed and result.modified == ["docs/a.txt"]


def test_verify_detects_missing_and_unexpected(evidence):
    manifest.write_manifest(evidence)
    (evidence / "b.bin").unlink()
    (evidence / "planted.txt").write_text("x")
    result = manifest.verify_manifest(evidence)
    assert result.missing == ["b.bin"]
    assert result.unexpected == ["planted.txt"]


def test_missing_manifest_raises(evidence):
    with pytest.raises(FileNotFoundError):
        manifest.verify_manifest(evidence)


@pytest.mark.parametrize("bad", ["nothex  file", "a" * 64 + " file", "A" * 64 + "  file"])
def test_malformed_lines_rejected(bad):
    with pytest.raises(ValueError):
        manifest.parse_manifest(bad + "\n")


def test_duplicate_entries_rejected():
    line = "a" * 64 + "  f\n"
    with pytest.raises(ValueError):
        manifest.parse_manifest(line + line)


def test_binary_marker_and_crlf_accepted():
    entries = manifest.parse_manifest("a" * 64 + "  *f.bin\r\n")
    assert entries == {"f.bin": "a" * 64}


@pytest.mark.skipif(shutil.which("sha256sum") is None, reason="sha256sum not installed")
def test_compatible_with_gnu_sha256sum(evidence):
    """Students can verify by hand with `sha256sum -c MANIFEST.sha256`."""
    manifest.write_manifest(evidence)
    proc = subprocess.run(["sha256sum", "-c", manifest.DEFAULT_NAME], cwd=evidence,
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cli_exit_codes(evidence, capsys):
    assert manifest.main(["create", str(evidence)]) == 0
    assert manifest.main(["verify", str(evidence)]) == 0
    (evidence / "b.bin").write_bytes(b"changed")
    assert manifest.main(["verify", str(evidence)]) == 1
    assert "MODIFIED    b.bin" in capsys.readouterr().out
