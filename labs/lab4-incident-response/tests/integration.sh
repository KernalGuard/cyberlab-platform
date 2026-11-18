#!/usr/bin/env bash
# Lab 4 container integration test (maintainers/CI only; students never run this).
# Requires: Docker with Compose v2 and the ir-workstation image built or pulled.
# Exercises the student workflow on the public demo evidence (E01 -> verified raw working
# copy -> Sleuth Kit and sqlite3; tshark on the capture; jq on the site logs) plus isolation,
# resources, reset and teardown. Asserts no case answers.
# Bash 3.2 compatible (macOS /bin/bash).
set -euo pipefail
cd "$(dirname "$0")/.."

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; exit 1; }
warn() { printf '  \033[33mWARN\033[0m %s\n' "$1"; }
run()  { docker compose run --rm -T workstation bash -c "$1" 2>/dev/null; }
scratch="work/laptop.raw work/laptop.raw.info work/unalloc.bin work/body.txt work/places.sqlite work/cookies.sqlite"

echo "Lab 4 integration test"
unset CYBERLAB_EVIDENCE
if [ "$(uname -s)" = "Linux" ]; then
  if [ "$(id -u)" != "0" ]; then
    export CYBERLAB_UID="$(id -u)" CYBERLAB_GID="$(id -g)"
  else
    chown 1000:1000 work
  fi
fi
out="$(mktemp)"; trap 'rm -f "$out" $scratch' EXIT

# environment + evidence integrity
docker compose run --rm -T verify >"$out" 2>&1 || { cat "$out"; fail "verify returned non-zero"; }
grep -qE "OVERALL: (PASS|WARN)" "$out" || fail "verify overall"
grep -q "\[PASS\] evidence-integrity" "$out" && pass "verify passes; evidence matches manifest" || fail "evidence integrity"
grep -q "\[PASS\] tools" "$out" && pass "all required tools present" || fail "tools"
[ -s work/lab4-check.json ] && pass "lab4-check.json written" || fail "lab4-check.json missing"

start=$SECONDS; run true; elapsed=$((SECONDS - start))
[ "$elapsed" -lt 10 ] && pass "container starts in ${elapsed}s (< 10 s)" || fail "startup took ${elapsed}s"

# Part A/B: E01 verification and an MD5-checked working copy in /work
run "ewfverify -q /evidence/hosts/coordinator-laptop.E01 >/dev/null 2>&1" && pass "ewfverify laptop E01" || fail "ewfverify"
res="$(run "ewfexport -q -u -f raw -t /work/laptop /evidence/hosts/coordinator-laptop.E01 >/dev/null 2>&1; e=\$(ewfinfo /evidence/hosts/coordinator-laptop.E01 | awk '/MD5/{print \$2}'); r=\$(md5sum /work/laptop.raw | cut -c1-32); [ \"\$e\" = \"\$r\" ] && echo match")"
[ "$res" = "match" ] && pass "working copy MD5 equals the E01's stored MD5" || fail "working copy MD5"

L=/work/laptop.raw
for cmd in "fsstat $L" "fls -r -p $L" "fls -r -d -p $L" "blkls $L"; do
  rc="$(run "$cmd >/dev/null 2>&1; echo \$?")"
  [ "$rc" = "0" ] && pass "$cmd (exit 0)" || fail "$cmd exit $rc"
done
[ "$(run "fls -r -d -p $L | grep -c OrphanFiles")" -ge 2 ] && pass "deleted files listed as orphans" || fail "orphans"
[ "$(run "istat -z UTC $L \$(fls -r -d -p $L | awk '/OrphanFile-/{print \$3; exit}' | tr -d :) | grep -c '(UTC)'")" -ge 1 ] && pass "istat -z UTC prints UTC times" || fail "istat -z UTC"
[ "$(run "icat $L \$(ifind -n /etc/passwd $L) | grep -c ':1000:'")" = "1" ] && pass "icat reads /etc/passwd by path" || fail "icat passwd"
res="$(run "for f in places cookies; do icat $L \$(fls -r -p $L | awk -v f=\$f.sqlite '\$NF ~ f {print \$2}' | tr -d :) > /work/\$f.sqlite; done; sqlite3 /work/places.sqlite 'SELECT count(*) FROM moz_historyvisits'; sqlite3 /work/cookies.sqlite 'SELECT count(*) FROM moz_cookies'")"
[ "$(echo "$res" | wc -l | tr -d ' ')" = "2" ] && [ "$(echo "$res" | head -1)" -ge 1 ] && pass "Firefox databases extracted and readable with sqlite3" || fail "sqlite3 ($res)"
[ "$(run "blkls $L > /work/unalloc.bin && strings -n 6 /work/unalloc.bin | grep -c '^#!/bin/sh'")" -ge 1 ] && pass "carving unallocated space finds the deleted script" || fail "carving"
[ "$(run "fls -r -m / $L > /work/body.txt && mactime -b /work/body.txt -z UTC -d 2>/dev/null | wc -l" | tr -d ' ')" -gt 10 ] && pass "mactime timeline" || fail "mactime"

# Part C: the capture
P=/evidence/network/office-edge.pcapng
# exit status, not stderr: on CI runners (no passwd entry for the UID, no HOME) tshark prints
# harmless profile-directory notices on stderr; frame-level problems are checked just below.
res="$(run "tshark -r $P >/dev/null 2>/work/tshark.err; echo \$?")"
[ "$res" = "0" ] && pass "tshark reads the capture (exit 0)" || { cat work/tshark.err; fail "tshark exit $res"; }
[ -s work/tshark.err ] && warn "tshark stderr: $(head -1 work/tshark.err)"
rm -f work/tshark.err
[ "$(run "tshark -r $P -Y '_ws.malformed || _ws.expert.severity >= warning' 2>/dev/null | wc -l" | tr -d ' ')" = "0" ] && pass "no malformed or warning-level frames" || fail "malformed frames"
[ "$(run "tshark -r $P -Y http.request -T fields -e frame.time_utc 2>/dev/null | head -1 | grep -c UTC")" = "1" ] && pass "frame.time_utc available" || fail "frame.time_utc"
res="$(run "tshark -r $P -Y 'http.request.method==\"POST\" && !(http.host contains \"intranet\")' -T fields -e http.file_data 2>/dev/null | head -1 | xxd -r -p | base64 -d | head -1")"
[ "$res" = "# Netscape HTTP Cookie File" ] && pass "upload body decodes (http.file_data | xxd | base64)" || fail "upload decode ($res)"

# Part D/E/F: logs
for f in gateway app; do
  n="$(run "wc -l < /evidence/web/$f.jsonl" | tr -d ' ')"; j="$(run "jq -c . /evidence/web/$f.jsonl | wc -l" | tr -d ' ')"
  [ "$n" = "$j" ] && [ "$n" -gt 100 ] && pass "$f.jsonl: every line is valid JSON ($n records)" || fail "$f.jsonl JSON ($n/$j)"
done
[ "$(run "jq -s 'group_by(.session) | length' /evidence/web/gateway.jsonl")" -gt 1 ] && pass "jq -s grouping works (detection-rule mechanics)" || fail "jq -s"
res="$(run "python3 -c 'import base64,sys; s=sys.argv[1]; print(base64.urlsafe_b64decode(s+\"=\"*(-len(s)%4)).decode())' eyJraW5kIjoidGVzdCJ9")"
[ "$res" = '{"kind":"test"}' ] && pass "unb64 helper decodes URL-safe base64" || fail "unb64 ($res)"
[ "$(run "grep -c 'DETAIL:  parameters:' /evidence/web/postgres.log")" -ge 1 ] && pass "postgres.log has parameterised queries" || fail "postgres params"
[ "$(run "grep -c 'INSERT INTO public.donors' /evidence/db/snapshot.sql")" -ge 50 ] && pass "snapshot has donor rows" || fail "snapshot"
[ "$(run "grep -c 'Accepted' /evidence/server/auth.log")" -ge 1 ] && pass "auth.log readable" || fail "auth.log"
run 'cyberlab-findings validate /lab/work.template/findings.json' | grep PASS >/dev/null && pass "findings template validates" || fail "findings validate"

# peak memory of an analysis pass
peak="$(run "tshark -r $P -Y http.request -T fields -e http.host >/dev/null 2>&1; jq -s 'group_by(.session)|length' /evidence/web/gateway.jsonl >/dev/null; fls -r -p $L >/dev/null; cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo none")"
if [ "$peak" = "none" ] || [ -z "$peak" ]; then
  warn "memory.peak not available; peak memory not measured"
else
  mb=$((peak / 1024 / 1024))
  [ "$mb" -lt 1024 ] && pass "peak memory ${mb} MB (< 1024 MB)" || fail "peak memory ${mb} MB"
fi

# isolation and security baseline
run 'touch /evidence/x 2>&1; true' | grep -q "Read-only file system" && pass "evidence is read-only" || fail "evidence writable!"
[ -z "$(run 'for d in /sys/class/net/*/; do n=$(basename "$d"); [ "$n" = lo ] && continue; [ $(( $(cat "$d/flags") & 1 )) -eq 1 ] && echo "$n"; done; true')" ] && pass "no active network interfaces besides lo" || fail "network present"
[ "$(run 'id -u')" = "${CYBERLAB_UID:-1000}" ] && pass "runs as non-root UID ${CYBERLAB_UID:-1000}" || fail "uid"
run 'touch /usr/local/bin/x 2>&1; true' | grep -q "Read-only file system\|Permission denied" && pass "root filesystem not writable" || fail "rootfs writable"
mnt="$(run "mkdir -p /tmp/m; mount -o loop,ro $L /tmp/m >/dev/null 2>&1; echo \$?")"
[ "$mnt" != "0" ] && pass "mounting images is refused (exit $mnt)" || fail "image could be mounted"

# evidence unchanged after the analysis above
run 'cd /evidence && sha256sum -c --quiet MANIFEST.sha256' >/dev/null && pass "evidence hashes unchanged after analysis" || fail "evidence changed"

# reset and teardown (remove the large working files first so reset does not back them up)
rm -f $scratch
echo "scratch" > work/scratch.txt
docker compose run --rm -T reset >/dev/null 2>&1 || fail "reset"
[ -f work/findings.json ] && [ -f work/incident-report.md ] && [ ! -f work/scratch.txt ] && ls work/.backup/*/scratch.txt >/dev/null \
  && pass "reset restores templates (incl. incident-report.md) and backs up work" || fail "reset behaviour"
docker compose down --remove-orphans >/dev/null 2>&1
[ "$(docker ps -a --filter label=com.docker.compose.project=cyberlab-lab4 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no containers" || fail "containers remain"
[ "$(docker network ls --filter label=com.docker.compose.project=cyberlab-lab4 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no networks" || fail "networks remain"
echo "All Lab 4 integration checks passed."
