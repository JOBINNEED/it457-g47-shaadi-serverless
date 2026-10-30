#!/usr/bin/env bash
# Resume the stack for a presentation: remove the reserved-concurrency limit so functions
# use the account's unreserved concurrency again. shaadi-loadgen stays paused unless --all is given.
set -euo pipefail
source "$(dirname "$0")/_config.sh"
targets=("${SERVING_FUNCTIONS[@]}")
[ "${1:-}" = "--all" ] && targets=("${ALL_FUNCTIONS[@]}")
for fn in "${targets[@]}"; do
  aws lambda delete-function-concurrency --region "$REGION" --function-name "$fn"
  echo "resumed $fn"
done
echo "Presentation page: $API_URL/demo"
