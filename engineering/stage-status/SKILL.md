---
name: engineering-stage-status
description: >
  Live stage board for a multi-session project: which stages are running,
  waiting to be dispatched, waiting on the orchestrator to accept or record a
  verdict, or waiting to be merged — derived from git branches, worktrees and
  stage documents every time, never from a hand-maintained table. Use when the
  user asks what is running or what needs attention, or says "task-status",
  "stage status", "現在跑到哪", "哪些在跑", "哪些還沒派", "進度", "狀態板",
  "what's running", "what's left". Read-only: it reports, it does not record,
  accept, merge or dispatch.
license: MIT
---

# Stage Status

## Related skills

- `../work-flow/SKILL.md` — the stage lifecycle this board maps onto, and the
  one-worktree-per-session convention it reads.
- `../orchestrator/SKILL.md` — the review point that consumes this board.
- `../project-records/SKILL.md` — why the board is derived instead of written.

---

## Why a derived board

A status table somebody updates by hand is wrong within minutes of being
written, and it never says so. In the reference project one such table went
stale three times; another said a stage was "dispatched, not back" when its
result had been committed five minutes earlier.

**State that git already knows should be read from git.** A brief exists or
it does not; a report is committed on a branch or it is not; a branch is
merged or it is not. This board re-derives all of it on every run.

---

## Run it

```bash
python3 <this skill's directory>/stage_status.py --repo <project root>
#   --all    include closed stages
#   --json   machine-readable output
```

Standard library only. Nothing is written.

### What it assumes

| | Default | Override in `<repo>/.stage-status.json` |
|---|---|---|
| Stage documents | `docs/tasks/stage-<N>-<slug>[-result\|-verify\|-verify-result].md` | `tasks_dir` |
| Integration branch | the branch checked out in `--repo` | `main_branch` |
| Session branches | executor `s<N>`, verifier `s<N>v` | `executor_branch`, `verifier_branch` (use `{n}`) |
| Verdict register | rows `\| <N> \|` in `docs/tasks/README.md` carrying ✅／🔴／⏸ + **ACCEPT／REJECT／BLOCKED** | `register` (or `null`), `verdict_marker` (regex) |
| Old stages with no branch | shown | `hide_branchless_below: <N>` |
| Stall threshold | 60 minutes without a file change | `stale_minutes` |
| Live sessions | `claude agents --json` — a session named `s<N>`／`s<N>v` counts as running even before its worktree exists | `session_lister` (or `null`) |

The register is needed because a stage the orchestrator accepted itself has
no verdict file — only the register row says it is done.

---

## States

| State | Means | Whose move |
|---|---|---|
| `pending dispatch` | brief exists, no executor branch | the user dispatches |
| `running` | executor worktree exists, no report yet | wait |
| `done, awaiting acceptance` | report committed, no verify brief, no recorded verdict | orchestrator: accept it or write a verify brief |
| `verify pending dispatch` | verify brief exists, no verifier branch | the user dispatches |
| `verifying` | verifier worktree exists, no verdict yet | wait |
| `verdict X, awaiting record` | verdict file exists, register row has no verdict | orchestrator records it |
| `recorded, awaiting merge` | verdict recorded, a session branch is not in the integration branch | a merge stage |
| `closed, clean up` | recorded and merged, but a session worktree is still on disk or its background session is still alive (they go idle, they do not exit) | orchestrator: `git worktree remove` (refuses if anything is uncommitted — keep it that way) and `claude rm <id>` |
| `closed` | recorded and merged, no worktree left | — (hidden unless `--all`) |

---

## Presenting it

Group the rows for the user — they want to know **what needs them**:

| Group | States |
|---|---|
| 🏃 Running | `running`, `verifying` |
| 📋 Needs dispatching | `pending dispatch`, `verify pending dispatch` — say where the prompt is, or offer to write it |
| 🧭 Needs the orchestrator | `done, awaiting acceptance`, `verdict …, awaiting record` |
| 🔀 Needs merging | `recorded, awaiting merge` |
| 🧹 Needs cleanup | `closed, clean up` |

For each row give the stage number, one line on what the stage is (from the
register or the brief's title), and the activity column. Use the user's
language. End with one line: the suggested next move.

⛔ **Report only.** Do not record, accept, merge or dispatch from inside this
skill — each of those is a separate decision the orchestrator takes on
purpose.

---

## What it cannot see

- ⚠ **A session opened outside the session lister** (an IDE's own agent panel)
  that has not created its worktree yet shows as `pending dispatch`. When it
  matters, ask.
- ⚠ **A fresh worktree's change time is its creation time.** "Changed 1 min
  ago" means "alive or just created", not "making progress".
- ⚠ **A deleted worktree directory** (git marks it prunable) is treated as no
  worktree; committed work is still on its branch. `git worktree prune`
  clears the stale entries.
- ⛔ It reads whether files exist, not whether they are right. It never
  replaces reading the report.
