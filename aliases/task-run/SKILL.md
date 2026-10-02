---
name: task-run
description: >
  Short command for engineering-stage-run: launch every ready stage that has a
  prompt file as a background agent session, within the concurrency rules.
  Use when the user types /task-run, or says "task-run", "派出去", "幫我開
  session", "run them".
license: MIT
---

# /task-run

Alias. Load and follow **`engineering-stage-run`** — installed in the same skills
directory as this one (`<this skill's base directory>/../../engineering/stage-run/`).

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules win.
2. From the repository root, dry run first and show the user the plan (what launches, what is held and why):
   ```bash
   python3 <this skill's base directory>/../../engineering/stage-run/stage_run.py --dry-run
   ```
3. Then launch (same command without `--dry-run`) and list each session id with `claude agents` / `claude attach <id>`. Report in the user's language.
