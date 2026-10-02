---
name: task-new-bus
description: >
  Short command for engineering-stage-handoff: write the prompt for a new
  orchestrator ("bus") session to take over — opening order, standing rules,
  live board, decisions waiting on the user, this session's mistakes. Use when
  the user types /task-new-bus, or says "新總線", "交接", "開新的總線",
  "handoff".
license: MIT
---

# /task-new-bus

Alias. Load and follow **`engineering-stage-handoff`** (`<this skill's base directory>/../../engineering/stage-handoff/SKILL.md`).

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — its handoff section is the backbone.
2. Commit and push what this session owes, then run the board from the repository root:
   ```bash
   python3 <this skill's base directory>/../../engineering/stage-status/stage_status.py
   ```
3. Write the prompt per the skill's "Prompt shape", **in the user's language**, in one copyable block.
