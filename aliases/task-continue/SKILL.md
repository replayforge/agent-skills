---
name: task-continue
description: >
  Nudge every unfinished background session of this repo to keep going: list
  background sessions (claude agents --json --all) that are neither done nor
  still running, and resume each with the message "continue" under the same
  session id. For after an API rate limit or a daemon restart left sessions
  stopped mid-task. Use when the user types /task-continue, or says "叫它們繼續",
  "全部 continue", "rate limit 之後續跑", "resume the stuck sessions".
license: MIT
---

# /task-continue

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules win.
2. From the repository root, dry run and show the list to the user:
   ```bash
   bash <this skill's base directory>/continue.sh --dry-run
   ```
3. Before sending, check each listed session against the stage board (`/task-status`): a session whose stage already has a committed result, or whose branch is the base of a not-yet-dispatched stage, may commit more work on resume — point those out and let the user drop them.
4. Send (optionally a different message as the argument):
   ```bash
   bash <this skill's base directory>/continue.sh            # sends "continue"
   ```
   Report each id in the user's language; suggest `/task-status-awake` to wait.

⚠ Sessions in `busy`/`running` are skipped on purpose — `--resume` on a live session starts a copy.
⚠ States are filtered by exclusion; an unfamiliar state is treated as resumable. That is why step 2 is a dry run.
