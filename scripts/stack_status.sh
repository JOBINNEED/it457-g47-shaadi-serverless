#!/usr/bin/env bash
# Show each function's state: PAUSED (reserved concurrency 0), LIMITED (n) or RUNNING,
# plus memory size and last modified time.
set -euo pipefail
source "$(dirname "$0")/_config.sh"
printf "%-22s %-10s %-8s %s\n" FUNCTION STATE MEMORY LAST_MODIFIED
for fn in "${ALL_FUNCTIONS[@]}"; do
  rc=$(aws lambda get-function-concurrency --region "$REGION" --function-name "$fn" \
        --query ReservedConcurrentExecutions --output text 2>/dev/null || echo None)
  case "$rc" in None|"") state=RUNNING ;; 0) state=PAUSED ;; *) state="LIMITED($rc)" ;; esac
  read -r mem mod < <(aws lambda get-function-configuration --region "$REGION" --function-name "$fn" \
        --query '[MemorySize,LastModified]' --output text)
  printf "%-22s %-10s %-8s %s\n" "$fn" "$state" "${mem}MB" "$mod"
done
