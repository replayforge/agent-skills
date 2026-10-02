---
name: task-status
description: >
  Short command for engineering-stage-status: show which stages are running,
  waiting to be dispatched, waiting on the orchestrator, waiting to be merged,
  or need cleanup. Use when the user types /task-status, or says "task-status",
  "狀態", "現在跑到哪", "哪些在跑".
license: MIT
---

# /task-status

Alias. Load and follow **`engineering-stage-status`** — it is installed in the
same skills directory as this one (`<this skill's base directory>/../../engineering/stage-status/`).

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules win over the shared skill.
2. From the repository root (the session's working directory), run:
   ```bash
   python3 <this skill's base directory>/../../engineering/stage-status/stage_status.py
   ```
   Add `--all` if the user asks for everything.
3. Present it as `engineering-stage-status` → "Presenting it" says, **in the user's language**. Report only.

⚠ The `../../engineering/…` paths are resolved **physically**: this skill directory is a symlink into the agent-skills repo, so `..` climbs the repo, not the install directory. Do not "simplify" them to `../engineering-stage-status`.
