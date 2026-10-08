#!/usr/bin/env bash
# Poll the stage board until nothing is running, then print it and exit.
# Meant for Bash run_in_background: one notification at the end, no model
# turn per poll (unlike /loop).
#
#   wait.sh [--dispatch] [--until N[,M…]] [--stall] [interval_s=180] [max_s=10800]
#
# --dispatch  on every poll, first run stage-run (same caps as /task-run) so a
#             freed slot is refilled with the next stage that has a prompt file.
# --until     also wake as soon as one of these stages is no longer
#             running/verifying (the user is waiting on that one), without
#             waiting for the rest. Combine with --dispatch or run beside it.
#             A named stage counts as finished only after this watcher has seen
#             it running/verifying — a stage not dispatched yet is waited for.
# --stall     also wake when a running/verifying row is marked "possibly stalled"
#             (no file change for stale_minutes, set in .stage-status.json):
#             a session that is busy but stuck, e.g. a test waiting forever.
#
# exit 0  nothing running/verifying any more
# exit 3  a row is still running/verifying but its session went idle
#         (finished without committing a result, or stuck) — needs a human
# exit 4  max_s elapsed
# exit 2  the board itself failed
# exit 5  --dispatch, but another dispatching watcher already runs for this repo
# exit 6  --until: one of the named stages finished (others may still run)
# exit 7  --stall: a running/verifying row has had no file change for too long
dispatch=0
until_=""
stall=0
seen=" "
while [[ "${1:-}" == --* ]]; do
  case "$1" in
    --dispatch) dispatch=1; shift ;;
    --until) until_="${2:?--until needs stage numbers}"; shift 2 ;;
    --stall) stall=1; shift ;;
    *) echo "unknown option $1"; exit 2 ;;
  esac
done
interval="${1:-180}"; max="${2:-10800}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
board="$here/../../engineering/stage-status/stage_status.py"
run="$here/../../engineering/stage-run/stage_run.py"
if (( dispatch )); then
  # Two dispatching watchers on one repo would launch the same stage twice.
  lock="/tmp/stage-dispatch-$(printf '%s' "$PWD" | cksum | cut -d' ' -f1)"
  if ! mkdir "$lock" 2>/dev/null; then
    other="$(cat "$lock/pid" 2>/dev/null)"
    if [[ -n "$other" ]] && kill -0 "$other" 2>/dev/null; then
      echo "ALREADY DISPATCHING (pid $other) — not starting a second watcher"; exit 5
    fi
    rm -rf "$lock"; mkdir "$lock"   # stale: its owner is gone
  fi
  echo $$ > "$lock/pid"
  trap 'rm -rf "$lock"' EXIT
fi
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
  # --until: a named stage not seen running yet (not dispatched) keeps us waiting.
  pending=""
  for n in ${until_//,/ }; do
    [[ "$seen" == *" $n "* ]] || printf '%s\n' "$busy" | grep -qE "^ +$n " || pending=1
  done
  [[ -z "$busy" && -z "$pending" ]] && { echo "ALL DONE"; echo "$out"; exit 0; }
  for n in ${until_//,/ }; do
    if printf '%s\n' "$busy" | grep -qE "^ +$n "; then
      seen="$seen$n "
    elif [[ "$seen" == *" $n "* ]]; then
      echo "STAGE $n FINISHED"; echo "$out"; exit 6
    fi
  done
  if (( stall )) && printf '%s\n' "$busy" | grep -q 'possibly stalled'; then
    echo "STALLED (no file change for stale_minutes)"; echo "$out"; exit 7
  fi
  # A verifying row lists the executor's session (idle, its work is done) next to
  # the verifier's (busy). Only a row with an idle session and no busy one is stuck.
  stuck="$(printf '%s\n' "$busy" | grep ':idle(' | grep -v ':busy(' || true)"
  [[ -n "$stuck" ]] && { echo "SESSION IDLE BUT STAGE NOT DONE"; echo "$out"; exit 3; }
  (( $(date +%s) - start >= max )) && { echo "TIMEOUT after ${max}s"; echo "$out"; exit 4; }
  sleep "$interval"
done
