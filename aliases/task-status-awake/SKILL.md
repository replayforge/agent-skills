---
name: task-status-awake
description: >
  Watch the stage board in the background and wake up when every running stage
  is done: poll engineering-stage-status every 3 minutes, stop when nothing is
  running or verifying (or a session went idle without a result, or 3 hours
  passed), then show the board and suggest the next command. With --dispatch it
  also refills freed slots with ready stages as it goes. Use when the user
  types /task-status-awake, or says "幫我盯著", "跑完叫我", "監控狀態",
  "wake me when done", "watch the stages".
license: MIT
---

# /task-status-awake

Wait for the running stages without spending a model turn per check.

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules win.
2. From the repository root, start the watcher with **Bash `run_in_background: true` and `timeout: 7200000`** (one notification when it exits):
   ```bash
   bash <this skill's base directory>/wait.sh 180 7100
   ```
   Arguments: poll interval and upper bound in seconds. Use the user's numbers if they gave any.
   🔴 **Set `timeout: 7200000`.** A background Bash command without it is killed at the default 30 minutes, long before the watcher's own bound — and the kill looks like an ordinary exit. 7200000 ms is the maximum, so keep the upper bound ≤ 7100 s; re-run the watcher when it reports `TIMEOUT`.
   **`--dispatch`** (first argument, `wait.sh --dispatch 180 7100`): on every poll, first run `engineering-stage-run` with its normal caps, so a slot freed by a finished stage is refilled with the next stage that has a prompt file; each launch is logged with its time. Use it when the user has asked for automatic refill (or the project notes say so) — launching sessions is otherwise the user's call via `/task-run`.
   **`--until N[,M]`**: also wake as soon as one named stage is no longer running/verifying — for when the user asked to be told early about that one stage. It takes no lock, so it can run **beside** an existing `--dispatch` watcher (`wait.sh --until 132 60 7100`). A named stage counts as finished only after the watcher has seen it running — a stage not yet dispatched is waited for.
   **`--stall`**: also wake (exit 7) when a running row is marked `possibly stalled` (no file change for `stale_minutes`, default 60, set in `.stage-status.json`) — a busy session stuck on, e.g., a test that waits forever.
   ⛔ Do not use `/loop` or `ScheduleWakeup` for this — they cost a full model turn on every poll.
3. Tell the user, in their language, what is being watched (the running rows) and that you will report when it ends. Then stop.
4. When the background command exits, read its output and report by exit code:

   | exit | meaning | suggest |
   |---|---|---|
   | 0 `ALL DONE` | nothing running or verifying | `/task-next` (records, acceptance, next brief) |
   | 3 `SESSION IDLE…` | a stage is still "running" but its session is idle — no result committed | `claude attach <id>` to look; do not assume it finished |
   | 4 `TIMEOUT` | upper bound reached, still running | re-run `/task-status-awake`, or check with `claude logs <id>` |
   | 2 | the board script failed | show the error |
   | 5 `ALREADY DISPATCHING` | another `--dispatch` watcher already runs for this repo | nothing — that one will notify; do not start a second |
| 6 `STAGE N FINISHED` | `--until N`: that stage left running/verifying (others may still run) | tell the user right away (they asked to be told early); read its verdict |
| 7 `STALLED` | `--stall`: a running row has not changed files for `stale_minutes` | `claude logs <id>`; look for a hung process (`ps`), do not assume progress |

   Show the board as `engineering-stage-status` → "Presenting it" says. Report only — do not run `/task-next` yourself unless the user asks.

⚠ It wakes when **all** running stages are done (with `--dispatch`: when nothing is running and nothing more could be launched). A stage opened by hand (an IDE panel) shows as running with no session — the watcher cannot see it end until its result is committed.
⚠ The `../../engineering/…` path inside `wait.sh` resolves **physically** (this directory is a symlink into the agent-skills repo).
