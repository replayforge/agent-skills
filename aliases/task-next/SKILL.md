---
name: task-next
description: >
  Short command for engineering-stage-next: take the orchestrator's next moves
  (record verdicts, self-accept what is mechanically checkable, clean up
  merged stages, write the next brief and prompt file) and stop at the first
  thing that needs the user. Use when the user types /task-next, or says
  "task-next", "繼續", "你繼續做", "下一步".
license: MIT
---

# /task-next

Alias. Load and follow **`engineering-stage-next`** — installed in the same skills
directory as this one (`<this skill's base directory>/../../engineering/stage-next/`) — together
with `engineering-orchestrator` and `engineering-work-flow`.

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules (who may dispatch, commit/push policy, language, register locations) win over the shared skill.
2. Run the board from the repository root:
   ```bash
   python3 <this skill's base directory>/../../engineering/stage-status/stage_status.py
   ```
3. Take "The turn" in `engineering-stage-next`. Stop at the first ⏸. Report in the user's language.
