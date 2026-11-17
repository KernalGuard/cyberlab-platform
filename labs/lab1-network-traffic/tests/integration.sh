#!/usr/bin/env bash
# Lab 1 container integration test (maintainers/CI only; students never run this).
# Requires: Docker with Compose v2 and the net-analysis image built or pulled.
# Covers AC-L1-04 to AC-L1-11 against the public demo evidence. It checks that the
# student guide's commands WORK; it deliberately asserts no case answers.
# Bash 3.2 compatible (macOS /bin/bash).
set -euo pipefail
cd "$(dirname "$0")/.."

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; exit 1; }
warn() { printf '  \033[33mWARN\033[0m %s\n' "$1"; }
run()  { docker compose run --rm -T workstation bash -c "$1" 2>/dev/null; }
P=/evidence/cedarwick-ws-segment.pcapng

echo "Lab 1 integration test"
unset CYBERLAB_EVIDENCE   # always test the demo evidence shipped in evidence/
if [ "$(uname -s)" = "Linux" ]; then
  if [ "$(id -u)" != "0" ]; then
    export CYBERLAB_UID="$(id -u)" CYBERLAB_GID="$(id -g)"
  else
    chown 1000:1000 work
  fi
fi

out="$(mktemp)"; trap 'rm -f "$out"' EXIT

# AC-L1-05 (start), environment
docker compose run --rm -T verify >"$out" 2>&1 || { cat "$out"; fail "verify returned non-zero"; }
grep -qE "OVERALL: (PASS|WARN)" "$out" || fail "verify overall"
grep -q "\[PASS\] evidence-integrity" "$out" && pass "verify passes; evidence matches manifest" || fail "evidence integrity"
[ -s work/lab1-check.json ] && pass "lab1-check.json written" || fail "lab1-check.json missing"

# AC-L1-08 startup (after pull/build)
start=$SECONDS; run true; elapsed=$((SECONDS - start))
[ "$elapsed" -lt 10 ] && pass "container starts in ${elapsed}s (< 10 s)" || fail "startup took ${elapsed}s"

# Tools and versions
run 'tshark --version | head -1' | grep "^TShark" >/dev/null && pass "tshark runs ($(run 'tshark --version | head -1'))" || fail "tshark"
run 'command -v capinfos editcap mergecap xxd base64 jq cyberlab-findings' >/dev/null && pass "guide tools present" || fail "guide tools missing"

# AC-L1-04: capture parses cleanly
[ "$(run "tshark -r $P -Y _ws.malformed | wc -l" | tr -d ' ')" = "0" ] && pass "no malformed packets" || fail "malformed packets present"
run "capinfos $P" | grep "pcapng" >/dev/null && pass "capinfos reads the capture" || fail "capinfos"

# Guide mechanics (no answers asserted)
run "tshark -r $P -t ud -c 1 -T fields -e _ws.col.Time" | grep -E "^20[0-9]{2}-[0-9]{2}-[0-9]{2} " >/dev/null && pass "-t ud prints UTC dates" || fail "-t ud format"
run "tshark -r $P -q -z io,phs" | grep "dns" >/dev/null && pass "protocol hierarchy statistics" || fail "io,phs"
[ "$(run "tshark -r $P -Y 'dns.flags.rcode == 3' | wc -l" | tr -d ' ')" -gt 0 ] && pass "NXDOMAIN filter matches" || fail "NXDOMAIN filter"
[ "$(run "tshark -r $P -Y 'http.request' -T fields -e http.user_agent | sort -u | wc -l" | tr -d ' ')" -gt 1 ] && pass "User-Agent field extraction" || fail "user-agent extraction"
decode='f=$(tshark -r '"$P"' -Y "http.content_type == \"application/octet-stream\" && http.request.method == \"POST\"" -T fields -e frame.number | head -1);
        tshark -r '"$P"' -Y "frame.number == $f" -T fields -e http.file_data | xxd -r -p > /tmp/u.b64 && base64 -d /tmp/u.b64 | file -b -'
run "$decode" | grep -i "CSV\|text" >/dev/null && pass "Part D decode pipeline (hex -> base64 -> text)" || fail "decode pipeline"
run "s=\$(tshark -r $P -Y http.request -T fields -e tcp.stream | head -1); tshark -r $P -q -z follow,http,ascii,\$s" | grep "HTTP/1.1" >/dev/null && pass "follow,http works" || fail "follow,http"
run 'cyberlab-findings validate /lab/work.template/findings.json' | grep PASS >/dev/null && pass "findings template validates" || fail "findings validate"

# AC-L1-09: peak memory of a full analysis pass, measured inside the container's cgroup
peak="$(run "tshark -r $P -q -z conv,ip -z endpoints,ip -z io,phs >/dev/null;
             tshark -r $P -Y 'http.request || dns' -T fields -e ip.src -e http.host -e dns.qry.name >/dev/null;
             cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo none")"
if [ "$peak" = "none" ] || [ -z "$peak" ]; then
  warn "memory.peak not available on this kernel; peak memory not measured"
else
  mb=$((peak / 1024 / 1024))
  [ "$mb" -lt 512 ] && pass "peak memory ${mb} MB (< 512 MB)" || fail "peak memory ${mb} MB"
fi

# AC-L1-06 / AC-L1-07 / security baseline
run 'touch /evidence/x 2>&1; true' | grep -q "Read-only file system" && pass "evidence is read-only" || fail "evidence writable!"
[ -z "$(run 'for d in /sys/class/net/*/; do n=$(basename "$d"); [ "$n" = lo ] && continue; [ $(( $(cat "$d/flags") & 1 )) -eq 1 ] && echo "$n"; done; true')" ] && pass "no active network interfaces besides lo" || fail "network present"
[ "$(run 'id -u')" = "${CYBERLAB_UID:-1000}" ] && pass "runs as non-root UID ${CYBERLAB_UID:-1000}" || fail "uid"
run 'touch /usr/local/bin/x 2>&1; true' | grep -q "Read-only file system\|Permission denied" && pass "root filesystem not writable" || fail "rootfs writable"
cap="$(run 'timeout 5 dumpcap -i lo -c 1 -w /tmp/x.pcapng >/dev/null 2>&1; echo $?')"
[ "$cap" != "0" ] && pass "live capture refused (dumpcap exit $cap)" || fail "live capture possible"

# AC-L1-05 (end): evidence unchanged after the analysis above
run 'cd /evidence && sha256sum -c --quiet MANIFEST.sha256' >/dev/null && pass "evidence hashes unchanged after analysis" || fail "evidence changed"

# AC-L1-10 reset
echo "scratch" > work/scratch.txt
docker compose run --rm -T reset >/dev/null 2>&1 || fail "reset"
[ -f work/findings.json ] && [ ! -f work/scratch.txt ] && ls work/.backup/*/scratch.txt >/dev/null && pass "reset restores template and backs up work" || fail "reset behaviour"

# AC-L1-11 teardown
docker compose down --remove-orphans >/dev/null 2>&1
[ "$(docker ps -a --filter label=com.docker.compose.project=cyberlab-lab1 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no containers" || fail "containers remain"
[ "$(docker network ls --filter label=com.docker.compose.project=cyberlab-lab1 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no networks" || fail "networks remain"
echo "All Lab 1 integration checks passed."
