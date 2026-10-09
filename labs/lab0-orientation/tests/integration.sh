#!/usr/bin/env bash
# Lab 0 container integration test (maintainers/CI only — students never run this).
# Requires: Docker with Compose v2, and the lab image built or pulled.
# Exercises every command the student guide depends on, plus reset and teardown.
set -euo pipefail
cd "$(dirname "$0")/.."

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; exit 1; }
run()  { docker compose run --rm -T workstation bash -c "$1" 2>/dev/null; }

echo "Lab 0 integration test"
# Linux hosts: run the container as the invoking user (as students are told to), unless that is root.
if [ "$(uname -s)" = "Linux" ]; then
  if [ "$(id -u)" != "0" ]; then
    export CYBERLAB_UID="$(id -u)" CYBERLAB_GID="$(id -g)"
  else
    chown 1000:1000 work
  fi
fi

out="$(mktemp)"; trap 'rm -f "$out"' EXIT
docker compose run --rm -T verify >"$out" 2>&1 || { cat "$out"; fail "verify returned non-zero"; }
grep -qE "OVERALL: (PASS|WARN)" "$out" || fail "verify overall"
pass "verify passes"
[ -s work/lab0-check.json ] && pass "lab0-check.json written" || fail "lab0-check.json missing"

[ "$(run 'file -b /evidence/documents/report.txt' | cut -d, -f1)" = "Zip archive data" ] && pass "file identifies disguised ZIP" || fail "file report.txt"
[ "$(run 'grep -c "Failed password" /evidence/logs/auth.log')" = "14" ] && pass "grep counts 14 failed logins" || fail "grep count"
run 'cd /evidence && sha256sum -c MANIFEST.sha256' >/dev/null && pass "manifest verifies by hand" || fail "manifest by hand"
[ "$(run 'cd /evidence && sha256sum -c transfer/sender_hashes.sha256 2>/dev/null | grep -c FAILED')" = "1" ] && pass "exactly one sender-hash mismatch" || fail "sender hash mismatch"
run 'touch /evidence/x 2>&1; true' | grep -q "Read-only file system" && pass "evidence is read-only" || fail "evidence writable!"
run 'ls /sys/class/net' | tr -d '\n' | grep -qx "lo" && pass "no network interfaces besides lo" || fail "network present"
[ "$(run 'id -u')" = "${CYBERLAB_UID:-1000}" ] && pass "runs as non-root UID ${CYBERLAB_UID:-1000}" || fail "uid"
run 'touch /usr/local/bin/x 2>&1; true' | grep -q "Read-only file system\|Permission denied" && pass "root filesystem not writable" || fail "rootfs writable"

echo "scratch" > work/scratch.txt
docker compose run --rm -T reset >/dev/null 2>&1 || fail "reset"
[ -f work/lab0-answers.md ] && [ ! -f work/scratch.txt ] && ls work/.backup/*/scratch.txt >/dev/null && pass "reset restores template and backs up work" || fail "reset behaviour"

docker compose down --remove-orphans >/dev/null 2>&1
[ "$(docker ps -a --filter label=com.docker.compose.project=cyberlab-lab0 -q | wc -l)" = "0" ] && pass "teardown leaves no containers" || fail "containers remain"
[ "$(docker network ls --filter label=com.docker.compose.project=cyberlab-lab0 -q | wc -l)" = "0" ] && pass "teardown leaves no networks" || fail "networks remain"
echo "All Lab 0 integration checks passed."
