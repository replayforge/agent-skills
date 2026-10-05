#!/usr/bin/env bash
# Poll the stage board until nothing is running, then print it and exit.
# Meant for Bash run_in_background: one notification at the end, no model
# turn per poll (unlike /loop).
#
#   wait.sh [--dispatch] [interval_s=180] [max_s=10800]
#
# --dispatch  on every poll, first run stage-run (same caps as /task-run) so a
#             freed slot is refilled with the next stage that has a prompt file.
#
# exit 0  nothing running/verifying any more
# exit 3  a row is still running/verifying but its session went idle
#         (finished without committing a result, or stuck) — needs a human
# exit 4  max_s elapsed
# exit 2  the board itself failed
dispatch=0
[[ "${1:-}" == "--dispatch" ]] && { dispatch=1; shift; }
interval="${1:-180}"; max="${2:-10800}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
board="$here/../../engineering/stage-status/stage_status.py"
run="$here/../../engineering/stage-run/stage_run.py"
start=$(date +%s)
while :; do
  if (( dispatch )); then
    r="$(python3 "$run" 2>&1)" || { echo "stage-run failed:"; echo "$r"; exit 2; }
    launched="$(printf '%s\n' "$r" | grep 'launched' || true)"
    # Give the new session time to appear on the board before reading it,
    # or the stage still looks "pending" and this poll could end as ALL DONE.
    [[ -n "$launched" ]] && { echo "$(date +%H:%M) $launched"; sleep 30; }
  fi
  out="$(python3 "$board" 2>&1)" || { echo "board failed:"; echo "$out"; exit 2; }
  busy="$(printf '%s\n' "$out" | grep -E '^ +[0-9]+ +(running|verifying) ' || true)"
  [[ -z "$busy" ]] && { echo "ALL DONE"; echo "$out"; exit 0; }
  # A verifying row lists the executor's session (idle, its work is done) next to
  # the verifier's (busy). Only a row with an idle session and no busy one is stuck.
  stuck="$(printf '%s\n' "$busy" | grep ':idle(' | grep -v ':busy(' || true)"
  [[ -n "$stuck" ]] && { echo "SESSION IDLE BUT STAGE NOT DONE"; echo "$out"; exit 3; }
  (( $(date +%s) - start >= max )) && { echo "TIMEOUT after ${max}s"; echo "$out"; exit 4; }
  sleep "$interval"
done
