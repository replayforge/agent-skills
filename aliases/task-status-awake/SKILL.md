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
2. From the repository root, start the watcher with **Bash `run_in_background: true`** (one notification when it exits):
   ```bash
   bash <this skill's base directory>/wait.sh 180 10800
   ```
   Arguments: poll interval and upper bound in seconds. Use the user's numbers if they gave any.
   **`--dispatch`** (first argument, `wait.sh --dispatch 180 10800`): on every poll, first run `engineering-stage-run` with its normal caps, so a slot freed by a finished stage is refilled with the next stage that has a prompt file; each launch is logged with its time. Use it when the user has asked for automatic refill (or the project notes say so) — launching sessions is otherwise the user's call via `/task-run`.
   ⛔ Do not use `/loop` or `ScheduleWakeup` for this — they cost a full model turn on every poll.
3. Tell the user, in their language, what is being watched (the running rows) and that you will report when it ends. Then stop.
4. When the background command exits, read its output and report by exit code:

   | exit | meaning | suggest |
   |---|---|---|
   | 0 `ALL DONE` | nothing running or verifying | `/task-next` (records, acceptance, next brief) |
   | 3 `SESSION IDLE…` | a stage is still "running" but its session is idle — no result committed | `claude attach <id>` to look; do not assume it finished |
   | 4 `TIMEOUT` | upper bound reached, still running | re-run `/task-status-awake`, or check with `claude logs <id>` |
   | 2 | the board script failed | show the error |

   Show the board as `engineering-stage-status` → "Presenting it" says. Report only — do not run `/task-next` yourself unless the user asks.

⚠ It wakes when **all** running stages are done (with `--dispatch`: when nothing is running and nothing more could be launched). A stage opened by hand (an IDE panel) shows as running with no session — the watcher cannot see it end until its result is committed.
⚠ The `../../engineering/…` path inside `wait.sh` resolves **physically** (this directory is a symlink into the agent-skills repo).
