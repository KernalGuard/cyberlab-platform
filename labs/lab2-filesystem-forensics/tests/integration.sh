#!/usr/bin/env bash
# Lab 2 container integration test (maintainers/CI only; students never run this).
# Requires: Docker with Compose v2 and the fs-forensics image built or pulled.
# Exercises the student workflow on the public demo evidence (E01 -> verified raw working
# copies -> Sleuth Kit) plus isolation, resources, reset and teardown. Asserts no case answers.
# Bash 3.2 compatible (macOS /bin/bash).
set -euo pipefail
cd "$(dirname "$0")/.."

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; exit 1; }
warn() { printf '  \033[33mWARN\033[0m %s\n' "$1"; }
run()  { docker compose run --rm -T workstation bash -c "$1" 2>/dev/null; }

echo "Lab 2 integration test"
unset CYBERLAB_EVIDENCE
if [ "$(uname -s)" = "Linux" ]; then
  if [ "$(id -u)" != "0" ]; then
    export CYBERLAB_UID="$(id -u)" CYBERLAB_GID="$(id -g)"
  else
    chown 1000:1000 work
  fi
fi
out="$(mktemp)"; trap 'rm -f "$out"; rm -f work/workstation.raw work/usb.raw work/*.raw.info work/unalloc.bin work/body.txt' EXIT

# environment + evidence integrity (start)
docker compose run --rm -T verify >"$out" 2>&1 || { cat "$out"; fail "verify returned non-zero"; }
grep -qE "OVERALL: (PASS|WARN)" "$out" || fail "verify overall"
grep -q "\[PASS\] evidence-integrity" "$out" && pass "verify passes; evidence matches manifest" || fail "evidence integrity"
[ -s work/lab2-check.json ] && pass "lab2-check.json written" || fail "lab2-check.json missing"

start=$SECONDS; run true; elapsed=$((SECONDS - start))
[ "$elapsed" -lt 10 ] && pass "container starts in ${elapsed}s (< 10 s)" || fail "startup took ${elapsed}s"

# Part A: E01 verification and MD5-checked working copies
for i in workstation usb; do
  run "ewfverify -q /evidence/$i.E01 >/dev/null 2>&1" && pass "ewfverify $i.E01" || fail "ewfverify $i.E01"
  res="$(run "ewfexport -q -u -f raw -t /work/$i /evidence/$i.E01 >/dev/null 2>&1; e=\$(ewfinfo /evidence/$i.E01 | awk '/MD5/{print \$2}'); r=\$(md5sum /work/$i.raw | cut -c1-32); [ \"\$e\" = \"\$r\" ] && echo match")"
  [ "$res" = "match" ] && pass "$i working copy MD5 equals the E01's stored MD5" || fail "$i working copy MD5"
done

# Sleuth Kit on the working copies exits cleanly (the E01 segfault workaround)
for cmd in "fsstat /work/workstation.raw" "fls -r -p /work/workstation.raw" "fls -r -d /work/workstation.raw" \
           "jls /work/workstation.raw" "fsstat /work/usb.raw" "fls -r -d /work/usb.raw" "blkls /work/workstation.raw"; do
  rc="$(run "$cmd >/dev/null 2>&1; echo \$?")"
  [ "$rc" = "0" ] && pass "$cmd (exit 0)" || fail "$cmd exit $rc"
done

# Guide mechanics (no answers asserted)
[ "$(run 'fls -r -d /work/workstation.raw | grep -c OrphanFiles')" -ge 1 ] && pass "deleted inodes listed as orphans (kernel-like deletion)" || fail "no orphans"
[ "$(run 'fls -r -d /work/usb.raw | cut -f2 | grep -c "^_"')" -ge 1 ] && pass "FAT deleted entry shows replaced first character" || fail "FAT deleted entry"
[ "$(run 'jls /work/workstation.raw | grep -c "Unallocated FS Block [0-9]"')" -ge 2 ] && pass "journal holds old metadata copies" || fail "journal copies"
[ "$(run 'blkls /work/workstation.raw > /work/unalloc.bin && strings /work/unalloc.bin | grep -c "@example.org"')" -ge 1 ] && pass "carving unallocated space finds deleted content" || fail "carving"
run 'fsstat /work/usb.raw' | grep "Volume ID: 0x" >/dev/null && pass "FAT volume ID readable" || fail "FAT fsstat"
[ "$(run 'fls -r -m / /work/workstation.raw > /work/body.txt && mactime -b /work/body.txt -d 2>/dev/null | wc -l' | tr -d ' ')" -gt 5 ] && pass "mactime timeline" || fail "mactime"
run 'cyberlab-findings validate /lab/work.template/findings.json' | grep PASS >/dev/null && pass "findings template validates" || fail "findings validate"

# peak memory of an analysis pass
peak="$(run "fls -r -p /work/workstation.raw >/dev/null; blkls /work/workstation.raw | strings >/dev/null; jls /work/workstation.raw >/dev/null; cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo none")"
if [ "$peak" = "none" ] || [ -z "$peak" ]; then
  warn "memory.peak not available; peak memory not measured"
else
  mb=$((peak / 1024 / 1024))
  [ "$mb" -lt 768 ] && pass "peak memory ${mb} MB (< 768 MB)" || fail "peak memory ${mb} MB"
fi

# isolation and security baseline
run 'touch /evidence/x 2>&1; true' | grep -q "Read-only file system" && pass "evidence is read-only" || fail "evidence writable!"
[ -z "$(run 'for d in /sys/class/net/*/; do n=$(basename "$d"); [ "$n" = lo ] && continue; [ $(( $(cat "$d/flags") & 1 )) -eq 1 ] && echo "$n"; done; true')" ] && pass "no active network interfaces besides lo" || fail "network present"
[ "$(run 'id -u')" = "${CYBERLAB_UID:-1000}" ] && pass "runs as non-root UID ${CYBERLAB_UID:-1000}" || fail "uid"
run 'touch /usr/local/bin/x 2>&1; true' | grep -q "Read-only file system\|Permission denied" && pass "root filesystem not writable" || fail "rootfs writable"
mnt="$(run 'mkdir -p /tmp/m; mount -o loop,ro /work/workstation.raw /tmp/m >/dev/null 2>&1; echo $?')"
[ "$mnt" != "0" ] && pass "mounting images is refused (exit $mnt)" || fail "image could be mounted"

# evidence unchanged after the analysis above
run 'cd /evidence && sha256sum -c --quiet MANIFEST.sha256' >/dev/null && pass "evidence hashes unchanged after analysis" || fail "evidence changed"

# reset and teardown (remove the large working files first so reset does not back them up)
rm -f work/workstation.raw work/usb.raw work/*.raw.info work/unalloc.bin work/body.txt
echo "scratch" > work/scratch.txt
docker compose run --rm -T reset >/dev/null 2>&1 || fail "reset"
[ -f work/findings.json ] && [ ! -f work/scratch.txt ] && ls work/.backup/*/scratch.txt >/dev/null && pass "reset restores template and backs up work" || fail "reset behaviour"
docker compose down --remove-orphans >/dev/null 2>&1
[ "$(docker ps -a --filter label=com.docker.compose.project=cyberlab-lab2 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no containers" || fail "containers remain"
[ "$(docker network ls --filter label=com.docker.compose.project=cyberlab-lab2 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no networks" || fail "networks remain"
echo "All Lab 2 integration checks passed."
