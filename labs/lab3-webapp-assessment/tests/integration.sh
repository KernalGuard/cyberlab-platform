#!/usr/bin/env bash
# Lab 3 container integration test (maintainers/CI only; students never run this).
# Requires Docker with Compose v2 and the four Lab 3 images built or pulled.
# Checks the Pattern B isolation, the student workflow, that each training weakness is
# present (mechanics only: asserts no variant answers), logging, reset and teardown.
# Bash 3.2 compatible (macOS /bin/bash).
set -euo pipefail
cd "$(dirname "$0")/.."

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; docker compose logs --tail 20 2>/dev/null || true; exit 1; }
ws()   { docker compose run --rm -T workstation bash -c "$1" 2>/dev/null; }
svc()  { docker compose exec -T "$1" sh -c "$2" 2>/dev/null; }
SITE=http://127.0.0.1:8080

echo "Lab 3 integration test"
unset CYBERLAB_EVIDENCE
if [ "$(uname -s)" = "Linux" ]; then
  if [ "$(id -u)" != "0" ]; then export CYBERLAB_UID="$(id -u)" CYBERLAB_GID="$(id -g)"; else chown 1000:1000 work; fi
fi
trap 'docker compose down -v --remove-orphans >/dev/null 2>&1 || true' EXIT
docker compose down -v --remove-orphans >/dev/null 2>&1 || true

# setup as a student would: reset, sign, start
docker compose run --rm -T reset >/dev/null 2>&1 || fail "reset"
[ -f work/authorized-use.md ] && pass "reset provides the authorised-use agreement" || fail "agreement template missing"
out="$(docker compose run --rm -T verify 2>&1 || true)"
echo "$out" | grep -q "\[FAIL\] authorized-use" && pass "verify refuses an unsigned agreement" || fail "unsigned agreement accepted"
sed -i.bak 's/^Name:.*/Name: CI Integration Test/' work/authorized-use.md && rm -f work/authorized-use.md.bak
printf 'I AGREE\n' >> work/authorized-use.md
docker compose up -d --wait --wait-timeout 120 >/dev/null 2>&1 || fail "stack did not become healthy"
pass "db, app and gateway healthy"

out="$(docker compose run --rm -T verify 2>&1)" || { echo "$out"; fail "verify returned non-zero"; }
for c in "evidence-integrity" "egress-blocked" "http:site" "authorized-use" "network-isolation"; do
  echo "$out" | grep -q "\[PASS\] $c" && pass "verify: $c" || { echo "$out"; fail "verify: $c"; }
done

# isolation (SEC-05/06)
[ "$(docker compose port gateway 8080)" = "127.0.0.1:8080" ] && pass "gateway published on 127.0.0.1 only" || fail "gateway binding"
[ "$(curl -s -o /dev/null -w '%{http_code}' $SITE/healthz)" = "200" ] && pass "site reachable from the host on 127.0.0.1:8080" || fail "host cannot reach site"
for s in app db; do
  r="$(svc $s "python3 -c \"import socket; socket.create_connection(('1.1.1.1', 443), timeout=3)\" >/dev/null 2>&1 && echo open || echo blocked")"
  [ "$r" = "blocked" ] && pass "$s has no route to the internet" || fail "$s can reach the internet"
done
r="$(ws 'curl -s -m 3 -o /dev/null -w "%{http_code}" http://app:5000/healthz || true')"
[ "$r" != "200" ] && pass "workstation cannot reach the app directly (only via gateway)" || fail "workstation reaches app directly"
r="$(ws 'python3 -c "import socket; socket.create_connection((\"db\", 5432), timeout=3)" >/dev/null 2>&1 && echo open || echo blocked')"
[ "$r" = "blocked" ] && pass "workstation cannot reach the database" || fail "workstation reaches the database"

# hardening of the long-running services
for s in gateway app db; do
  [ "$(svc $s 'id -u')" = "1000" ] && pass "$s runs as UID 1000" || fail "$s uid"
  svc $s 'touch /usr/local/bin/x 2>&1; true' | grep -q "Read-only file system\|Permission denied" && pass "$s root filesystem not writable" || fail "$s rootfs writable"
done

# training weaknesses present (mechanics only)
mech="$(ws '
J=/tmp/j; S=$SITE
c=$(curl -s -c $J -b $J -o /dev/null -w "%{http_code}" -d "full_name=CI" -d "email=ci@example.com" -d "password=a" $S/register); echo "register1=$c"
echo "error=$(curl -s -b $J -o /tmp/e -w "%{http_code}" $S/receipts/x)$(grep -q "/app/app.py" /tmp/e && echo Y)"
echo "idor=$(curl -s -b $J $S/receipts/100001 | grep -c "Donation receipt")"
F=$(python3 -c "import base64,json; print(base64.urlsafe_b64encode(json.dumps({\"kind\":\"staff\",\"id\":1,\"n\":1}).encode()).decode().rstrip(\"=\"))")
echo "forged=$(curl -s -b "cw_session=$F" $S/staff | grep -c "Staff dashboard")"
echo "sqli=$(curl -s -o /dev/null -w "%{http_code}" -b "cw_session=$F" -G $S/staff/donors --data-urlencode "q='"'"'")"
')"
echo "$mech" | grep -q "register1=302" && pass "weak password policy present (1-character password accepted)" || fail "password policy: $mech"
echo "$mech" | grep -q "error=500Y" && pass "verbose error page present" || fail "verbose errors: $mech"
echo "$mech" | grep -q "idor=1" && pass "receipt IDOR present" || fail "IDOR: $mech"
echo "$mech" | grep -q "forged=1" && pass "forgeable session present" || fail "session: $mech"
echo "$mech" | grep -q "sqli=500" && pass "injectable search present" || fail "sqli: $mech"

# logs (Lab 3 Part F, Lab 4 evidence)
logs="$(ws 'ls /logs; grep -c "\"session\":\"ey" /logs/gateway.jsonl; grep -c "donor_search" /logs/app.jsonl; grep -c "ILIKE" /logs/postgres.log')"
for f in gateway.jsonl app.jsonl postgres.log; do echo "$logs" | grep -q "^$f$" && pass "log written: $f" || fail "missing log $f"; done
[ "$(echo "$logs" | tail -3 | awk '$1 > 0' | wc -l | tr -d ' ')" = "3" ] && pass "logs record sessions, searches and SQL" || fail "log content: $logs"

# resources
mem="$(docker stats --no-stream --format '{{.MemUsage}}' $(docker compose ps -q) | awk '{v=$1; u=v; gsub(/[0-9.]/,"",u); gsub(/[A-Za-z]/,"",v); if(u=="GiB")v*=1024; if(u=="KiB")v/=1024; s+=v} END{printf "%d", s}')"
[ "$mem" -lt 2048 ] && pass "stack memory ${mem} MB (< 2048 MB)" || fail "stack memory ${mem} MB"

# app restart (the remediation workflow) keeps the stack healthy
docker compose restart app >/dev/null 2>&1 && docker compose up -d --wait --wait-timeout 60 >/dev/null 2>&1 && pass "app restarts cleanly (remediation workflow)" || fail "app restart"

# evidence unchanged; reset; teardown
ws 'cd /evidence && sha256sum -c --quiet MANIFEST.sha256' >/dev/null && pass "evidence unchanged" || fail "evidence changed"
echo "scratch" > work/scratch.txt
docker compose run --rm -T reset >/dev/null 2>&1 || fail "reset"
[ ! -f work/scratch.txt ] && ls work/.backup/*/scratch.txt >/dev/null && pass "reset restores templates and backs up work" || fail "reset behaviour"
docker compose down -v --remove-orphans >/dev/null 2>&1
[ "$(docker ps -a --filter label=com.docker.compose.project=cyberlab-lab3 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no containers" || fail "containers remain"
[ "$(docker network ls --filter label=com.docker.compose.project=cyberlab-lab3 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no networks" || fail "networks remain"
[ "$(docker volume ls --filter label=com.docker.compose.project=cyberlab-lab3 -q | wc -l | tr -d ' ')" = "0" ] && pass "teardown leaves no volumes" || fail "volumes remain"
trap - EXIT
echo "All Lab 3 integration checks passed."
