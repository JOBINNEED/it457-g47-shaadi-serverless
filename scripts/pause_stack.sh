#!/usr/bin/env bash
# Pause the stack: set reserved concurrency to 0 on every function (same as "Throttle" in the console).
# Nothing is deleted; calls return HTTP 503 until resume_stack.sh is run.
set -euo pipefail
source "$(dirname "$0")/_config.sh"
for fn in "${ALL_FUNCTIONS[@]}"; do
  aws lambda put-function-concurrency --region "$REGION" \
      --function-name "$fn" --reserved-concurrent-executions 0 >/dev/null
  echo "paused  $fn"
done
echo "All functions throttled. Check: curl -s -o /dev/null -w '%{http_code}\n' $API_URL/baseline  (expect 503)"
