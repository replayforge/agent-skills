---
name: engineering-stage-run
description: >
  Dispatch every stage that is ready as its own background agent session,
  instead of the user opening a session and pasting each handoff prompt.
  Reads the live stage board, takes stages waiting to be dispatched that have
  a prompt file, applies the concurrency rules (one code stage at a time, one
  merge stage at a time, a total cap), and launches each with
  `claude --bg`. Use when the user says "task-run", "run them", "派出去",
  "幫我開 session", "dispatch", "start the ready stages". It launches
  sessions; it does not write briefs, accept results or settle decisions.
license: MIT
---

# Stage Run

## Related skills

- `../stage-status/SKILL.md` — the board this reads, and the session lister that makes launched sessions show as running before they create a worktree.
- `../stage-next/SKILL.md` — writes the briefs and the prompt files this skill launches.
- `../work-flow/SKILL.md` — one session, one worktree, one branch.

---

## Run it

```bash
python3 <this skill's directory>/stage_run.py --repo <project root> --dry-run   # show what would launch, and why the rest are held
python3 <this skill's directory>/stage_run.py --repo <project root>             # launch
#   --only 95,96   restrict to these stages
```

If `<repo>/.stage-status.json` names a `notes` file, read it first — project rules win. Always run `--dry-run` first and show the user the plan in one short table, then launch. Report each launched session's id and how to watch it:

```text
claude agents          list sessions and their status
claude attach <id>     open one in this terminal (it keeps running when you leave)
claude logs <id>       recent output
```

---

## What it needs from the orchestrator

A **prompt file** beside each brief — the handoff prompt, saved instead of pasted:

```text
stage-<N>-<slug>-prompt.md          → session s<N>
stage-<N>-<slug>-verify-prompt.md   → session s<N>v
```

First line declares the kind, which drives the concurrency rules:

```text
<!-- stage-run: kind=docs -->        docs | research | crate | merge
```

| Kind | Rule | Why |
|---|---|---|
| `crate` | at most `max_crate` (default 1) running | code stages share build caches and collide at merge |
| `merge` | at most `max_merge` (default 1) running | a merge stage moves the integration branch; nobody else may commit to it meanwhile |
| any | at most `max_parallel` (default 3) running | register writes and review capacity |

A running stage whose kind cannot be read (dispatched by hand, no prompt file) is **counted as `crate`** — the conservative choice; it can only hold a launch back.

Commit the prompt file with the brief. A stage with a brief but no prompt file is held with the reason shown.

---

## Configuration

In `<repo>/.stage-status.json` under `"run"`:

| Key | Default |
|---|---|
| `launcher` | `["claude", "--bg", "-n", "{name}", "--permission-mode", "bypassPermissions", "{prompt}"]` (cwd = repo root) |
| `max_parallel` / `max_crate` / `max_merge` | 3 / 1 / 1 |
| `background_note` | appended to every prompt: no human is watching — write open questions into the report and stop; commit only your own files; do not push |

⚠ **`bypassPermissions` is a real decision.** A background session has nobody to approve a permission prompt, so it would otherwise stall. Use it only where the user has chosen it, and keep the prompt's own limits (worktree, no push, read-only paths) — they are the remaining guard.

---

## What it will not do

- ⛔ Launch a stage without a prompt file, or one whose session name is already live.
- ⛔ Exceed the concurrency rules — held stages are listed with the reason; run it again when something finishes.
- ⛔ Write briefs, accept, record or merge. That is `stage-next` / the orchestrator.
- ⚠ It cannot see sessions opened outside the session lister (an IDE's own agent panel). If the user also dispatches by hand, check the board's worktree column before launching.
