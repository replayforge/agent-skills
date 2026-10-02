---
name: engineering-stage-handoff
description: >
  Hand the orchestrator role to a fresh session: produce one prompt the user
  pastes into a new session so it can take over as the coordinating session
  without reading this conversation. Combines what does not rot (the
  project's opening order, standing rules, where state lives) with what was
  measured just now (the live stage board, decisions waiting on the user,
  what this session got wrong). Use when the user says "task-new-bus",
  "新總線", "交接", "開新的總線", "handoff", "hand over", "the context is
  getting long". It writes the prompt; it does not dispatch the new session.
license: MIT
---

# Stage Handoff

## Related skills

- `../orchestrator/SKILL.md` — the role being handed over.
- `../stage-status/SKILL.md` — the live part of the prompt comes from the board, not from memory.
- `../project-records/SKILL.md` — why the prompt points at registers instead of copying them.

---

## Why a handoff prompt, and what must not go in it

A new orchestrator that starts by reading the old conversation pays for every
token of it and inherits its confusions. One that starts from a prompt gets
**the opening order and the live state, nothing else** — and reads the rest
from the registers, which are the source of truth.

The failure to avoid: **a status table pasted into the prompt.** It is true
for minutes. Every row the new session could get from the board or a
register must be a **pointer**, not a copy. The prompt carries a snapshot of
state only as "measured at <time> on <commit> — re-run the board, do not
trust this".

---

## Build it

```text
0. If <repo>/.stage-status.json names a `notes` file, read it — its handoff section
   (opening order, standing rules) is the backbone of the prompt.
1. Commit and push everything this session owes first. A handoff with uncommitted
   register edits hands over a lie.
2. Run the stage board (../stage-status/stage_status.py). Note the commit it ran on.
3. Collect, from this session — these exist nowhere else yet:
   - decisions the user still has to answer (each with the question, options, your recommendation)
   - what is running or dispatched right now, and what to do when each returns
   - mistakes this session made that the next one is likely to repeat, each with its mechanism
   - standing instructions the user gave this session that are not yet in the notes file or a register
     → put them in the notes file or a register now, then point at them
4. Write the prompt (shape below). Print it in one copyable block.
```

### Prompt shape

```text
You are the orchestrator (coordinating session) of <project>.

Opening order — do not skip:
1. Load engineering-work-flow, read it whole. Then engineering-orchestrator. Load
   engineering-verification when you accept something yourself.
2. Read <notes file> and <handoff doc, if the project has one>.
3. <project-specific orientation reads, from the notes file>
4. Run /task-status (or the board script). The board is the authority on what is
   running; the register is the authority on verdicts.

Standing rules (from the notes file — repeat only the few that cause damage if missed):
- …

State measured <time> on <commit> — ⚠ re-run the board, do not trust this:
- running: …
- waiting on the user: …
- next moves when each returns: …

Mistakes the previous orchestrator made (mechanism, not narrative):
- …

Waiting on the user (do not settle these):
- <question> — options — recommendation
```

Keep it under a page. Everything longer belongs in a register the prompt points at.

---

## Checks before handing it over

- [ ] `git status` is clean for every path this session touched, and pushed if the project pushes.
- [ ] Every state line in the prompt is either a pointer or carries "measured at <time> on <commit>".
- [ ] Every standing instruction the user gave in this session is in the notes file or a register — **not only in the prompt**.
- [ ] Every open decision names its owner. An unowned question in a handoff is a forgotten question.

---

## What it will not do

- ⛔ Start the new session (the user opens it — it needs a fresh context, not a background worker).
- ⛔ Copy registers or status tables into the prompt.
- ⛔ Settle the open decisions it lists.
