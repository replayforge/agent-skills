---
name: engineering-stage-next
description: >
  Advance the project by one orchestrator turn without being told what to do:
  read the live stage board, then take every move that belongs to the
  orchestrator — record verdicts, self-accept what is mechanically checkable,
  clean up merged worktrees, write the next brief and its handoff prompt —
  and stop at the first thing that needs the user (a decision, a dispatch, a
  question the board cannot answer). Use when the user says "task-next",
  "next", "繼續", "下一步你做", "你繼續做", "keep going", "advance". It never
  dispatches sessions itself and never settles an open decision.
license: MIT
---

# Stage Next

## Related skills

- `../stage-status/SKILL.md` — the board this skill reads first. **Run it; do not reason from memory of the last board.**
- `../orchestrator/SKILL.md` — every move below is an orchestrator move and follows that skill (pre-flight, briefs, acceptance clauses that can go red, the review-point questions).
- `../verification/SKILL.md` — whenever this turn accepts something itself.
- `../work-flow/SKILL.md` — lifecycle, one worktree per session, merge stages.
- `../stage-run/SKILL.md` — launches the prompt files this turn writes, as background sessions.

---

## The turn

```text
1. Run the stage board.
2. For each row, in this order, take the move in the table below.
3. Stop at the first move marked ⏸ — finish the row you are on, do not start another.
4. Report: what you did (with commits), what is now waiting, and the one thing you need from the user.
```

Order matters: **records and acceptance first, then cleanup, then new work.** A new brief written before an outstanding verdict is recorded may be built on a premise that verdict just overturned.

| Board state | Move | Stops? |
|---|---|---|
| `verdict X, awaiting record` | Read the verdict file. Record it in the register with its reason, what it overturned, and what it hands to the next stage. If it overturns a premise of a not-yet-dispatched stage, mark that stage `INVALIDATED`/`SUPERSEDED` (orchestrator §3). If the verdict triggers a recorded **reopen condition** of a decision ⇒ prepare the question for the user | ⏸ if a decision reopened |
| `done, awaiting acceptance` | Decide self-verify vs separate verification (orchestrator §5). Self-verify **only** when every load-bearing claim re-runs as one command, no build is needed, and you did not author it — then re-run, record ACCEPT/REJECT with what you ran. Otherwise write the verify brief and its prompt | ⏸ if a verify prompt was written |
| `recorded, awaiting merge` | Collect every such stage; write one merge-stage brief and prompt (tip SHAs, expected per-file blobs, a missed-merge control that goes red) | ⏸ (merge is dispatched) |
| `closed, clean up` | `git worktree remove <path>` — never `--force`; it refuses if anything is uncommitted, which is the check. Keep the branch. `claude rm <id>` any session still alive for that stage | no |
| `pending dispatch`, `verify pending dispatch` | Make sure the **prompt file** (`stage-<N>-<slug>[-verify]-prompt.md`, first line `<!-- stage-run: kind=… -->`) exists and is current. If the project uses `../stage-run/SKILL.md`, offer to launch; otherwise hand the prompt over. Ask whether it is already running if the board cannot tell | ⏸ |
| `running`, `verifying` | Nothing. Note how long since the last change; past the stall threshold, ask | no |
| board empty of orchestrator moves | Pick the next highest-value unblocked stage (orchestrator §5 "What you decide") and write its brief and prompt | ⏸ (dispatch) |

After the moves: commit only the paths you changed (`git commit -- <paths>`), and push if the project has authorized that. While a merge stage is fast-forwarding the integration branch, do not commit to it — wait.

---

## Hard stops — never cross these inside this skill

- ⛔ **An open decision.** Prepare the question (options, evidence, a recommendation); do not pick.
- ⛔ **Dispatching a session from inside this skill.** Write the prompt file; launching is `stage-run`, and only when the user asks for it. Do not spawn in-conversation agents to do stage work.
- ⛔ **Accepting what you authored**, or anything touching shipping code, money, protocol or security, or a verdict that changes project direction — those get a separate verification session.
- ⛔ **A brief whose premise you have not re-checked against the latest verdicts.**
- ⛔ **Destructive cleanup beyond merged worktrees** (branches, other people's trees, `--force`).

If the turn ends with nothing for the user to do, say so — and say what will arrive next.

---

## Report shape

```text
Done this turn      <move> — <stage> — <commit>
Waiting             <stage>: <state> (running / verifying …)
Needs you           <the one decision or dispatch>, with the prompt or the question
```

Keep it short. The registers hold the detail; the user wants to know what changed and what they must do.
