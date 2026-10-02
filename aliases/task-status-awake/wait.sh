#!/usr/bin/env bash
# Poll the stage board until nothing is running, then print it and exit.
# Meant for Bash run_in_background: one notification at the end, no model
# turn per poll (unlike /loop).
#
#   wait.sh [interval_s=180] [max_s=10800]
#
# exit 0  nothing running/verifying any more
# exit 3  a row is still running/verifying but its session went idle
#         (finished without committing a result, or stuck) — needs a human
# exit 4  max_s elapsed
# exit 2  the board itself failed
interval="${1:-180}"; max="${2:-10800}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
board="$here/../../engineering/stage-status/stage_status.py"
start=$(date +%s)
while :; do
  out="$(python3 "$board" 2>&1)" || { echo "board failed:"; echo "$out"; exit 2; }
  busy="$(printf '%s\n' "$out" | grep -E '^ +[0-9]+ +(running|verifying) ' || true)"
  [[ -z "$busy" ]] && { echo "ALL DONE"; echo "$out"; exit 0; }
  printf '%s\n' "$busy" | grep -q ':idle(' && { echo "SESSION IDLE BUT STAGE NOT DONE"; echo "$out"; exit 3; }
  (( $(date +%s) - start >= max )) && { echo "TIMEOUT after ${max}s"; echo "$out"; exit 4; }
  sleep "$interval"
done
