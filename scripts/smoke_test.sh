#!/usr/bin/env bash
# Pre-presentation check: calls every public route once and reports status and latency.
# Uses only curl (no AWS login needed). Exit code 1 if any route fails.
set -uo pipefail
source "$(dirname "$0")/_config.sh"
fail=0
check() {  # name expected_status method path [json_body]
  local name=$1 want=$2 method=$3 path=$4 body=${5:-}
  local out
  if [ -n "$body" ]; then
    out=$(curl -s -o /tmp/smoke_body -w '%{http_code} %{time_total}' -X "$method" \
          -H 'Content-Type: application/json' -d "$body" "$API_URL$path")
  else
    out=$(curl -s -o /tmp/smoke_body -w '%{http_code} %{time_total}' -X "$method" "$API_URL$path")
  fi
  local code=${out% *} secs=${out#* }
  local ms; ms=$(awk "BEGIN{printf \"%d\", $secs*1000}")
  if [ "$code" = "$want" ]; then echo "OK    $name  HTTP $code  ${ms} ms"
  else echo "FAIL  $name  HTTP $code (wanted $want)  ${ms} ms"; head -c 200 /tmp/smoke_body; echo; fail=1; fi
}
check "presentation page " 200 GET  /demo
check "baseline          " 200 GET  /baseline
check "send interest     " 201 POST /interest '{"from":"smoke_test","to":"user_42","message":"pre-demo check"}'
check "photo moderation  " 200 POST /moderate '{"imageKey":"photos/photo_01.jpg"}'
[ $fail = 0 ] && echo "All routes OK. 503 means paused: run resume_stack.sh." || echo "Some routes failed (503 = paused)."
exit $fail
