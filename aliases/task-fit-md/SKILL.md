---
name: task-fit-md
description: >
  Short command for engineering-doc-fit: have a fresh session read a document
  cold as a named outside reader (e.g. a PM), list where it jumps, and fill the
  context from repository sources without changing any fact — checked by a
  script. Use when the user types /task-fit-md <path> [--reader …] [--<提示詞>],
  or says "以 PM 角度補脈絡", "讀起來很跳", "fit this doc".
license: MIT
---

# /task-fit-md

Alias. Load and follow **`engineering-doc-fit`** — installed in the same skills
directory as this one (`<this skill's base directory>/../../engineering/doc-fit/`).

Arguments: `<path>`, `--reader "<who>"` (ask if missing), and any other
`--<text>` is passed to the fresh session as extra instructions.
If the repo has `.stage-status.json` with a `notes` path, read it first —
project rules on committing and on launching sessions win.
