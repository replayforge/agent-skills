---
name: engineering-work-flow
description: >
  Coordinate multi-stage engineering work as the orchestration layer: inspect the
  real project state before dispatch, split work into independently reviewable
  stages, write evidence-backed task briefs and handoff prompts, route work to
  specialized executor roles, independently verify results, and update durable
  project registers. Use when planning, splitting, dispatching, auditing, or
  accepting engineering work across multiple sessions or agents. Designed to
  support dedicated implementation and verification role skills without embedding their implementation
  behavior into the orchestrator.
argument-hint: "[brief|verify|split|audit]"
license: MIT
---

# Engineering Work Flow

## Related skills

This skill is the workflow constitution. Role-specific and knowledge-persistence behavior lives in sibling engineering skills:

- `../orchestrator/SKILL.md` — coordination, decomposition, dispatch, acceptance, and project-state governance.
- `../implementation/SKILL.md` — implementation-session behavior, scope discipline, evidence-backed delivery, and blocker escalation.
- `../verification/SKILL.md` — independent/adversarial verification, regression reasoning, acceptance challenge, and evidence quality.
- `../research/SKILL.md` — evidence gathering dispatched before a decision or implementation can proceed.
- `../project-records/SKILL.md` — the form of the durable documents every role reads and writes.
- `../knowledge-capture/SKILL.md` — durable engineering knowledge extraction and persistence.

Do not duplicate the detailed rules of sibling skills here. This file defines how the roles interact.

Coordinate the engineering process. Do not collapse orchestration, implementation, and QA into one role.

This skill defines the **workflow contract** between roles. The internal rules of each role belong in that role's skill, not here.

## Role model

The workflow has four logical roles. **Only one of them coordinates.**

- **Orchestrator** — owns the **project model**, project state, the task graph and its dependency direction, sequencing, acceptance decisions, and the registers. It decides what happens next. It does not implement.
- **Research** — removes the uncertainty that prevents the orchestrator from decomposing or sequencing safely. Returns evidence, measurements, inference, unknowns, options and costs. The `research` skill owns its behavior. It does not decide.
- **Implementation** — constructs the requested change within the dispatched scope and reports evidence. The `implementation` skill owns implementation-session behavior without owning project-level scope or final acceptance.
- **Verification** — independently challenges behavior, acceptance criteria, regressions, evidence quality, and silent failure modes. The `verification` skill owns independent verification behavior. Its verdict returns to the orchestrator; it is not the end of the workflow.

Research, Implementation and Verification are **dispatched** sessions. Each returns a report to the orchestrator and stops there.

A session may temporarily perform more than one role only when explicitly requested, but **an artifact must not be independently certified by the same role/session that materially authored it**.

The orchestrator may inspect files, run commands, execute tests, and create temporary verification scripts. It should not modify the production artifact it intends to independently accept.

## Core invariant

**Reports are claims. Evidence is verification.**

Never accept an executor's statement merely because it is detailed, plausible, or says tests passed. Re-run the load-bearing assertions independently.

## 1. Workflow loop

```text
PROJECT_START
      │
      ▼
┌──────────────────────────────────────────────┐
│  ORCHESTRATOR REVIEW                         │ ◄─────────────┐
│  ─────────────────────────────────────────   │               │
│  read the incoming report + registers        │               │
│  update the project model                    │               │
│  decompose only as far as evidence supports  │               │
│  re-sequence; invalidate what is now stale   │               │
│  choose the next move                        │               │
└──────────────────────────────────────────────┘               │
      │                                                        │
      ├── evidence gap ──► RESEARCH ──► research report ───────┤
      │                                                        │
      ├── task brief ───► IMPLEMENTATION                       │
      │                        │                               │
      │                        ▼                               │
      │                 implementation report                  │
      │                        │                               │
      │                        ▼                               │
      │                 VERIFICATION  (independent)            │
      │                        │                               │
      │                        ▼                               │
      │            ACCEPT / REJECT / BLOCKED ──────────────────┘
      │
      └── nothing unblocked remains in scope ──► PROJECT_DONE
```

Three invariants hold this loop together:

- **The orchestrator review is the only decision point.** Research, Implementation and Verification each end by returning a report; none of them selects or dispatches the next piece of work.
- **Verification is never the endpoint.** Every accept, reject and block re-enters the review.
- **Research is re-enterable at every review**, not only at the start. A gap discovered during implementation or verification is a reason to dispatch research, not a reason to guess.

Never skip pre-flight for a dispatched stage. Never mark executor completion as accepted work without verification.

### Decomposition depth is bounded by evidence

The project is not split into tasks once. **Decompose only as far as current evidence supports**, leave more distant work coarse, and refine it at a later review when the upstream interface or boundary it depends on has actually been verified.

An initial decomposition is a hypothesis. Treat it as one.

## 2. Project state and registers

Prefer these durable project registers when the project is large enough to need them:

- `roadmap.md` — stages, dependencies, status, blockers, and next-ready work.
- `rules.md` — project-specific constraints with provenance.
- `findings.md` — verified observations and overturned findings.
- `decisions.md` — architecture/product/engineering decisions, rationale, rejected alternatives, evidence, and revisit conditions.

Do not create documents merely to satisfy this list. Reuse an existing project information architecture when it already serves the same purpose.

### Finding vs decision vs rule

Keep these distinct:

- **Finding:** what was observed and verified.
- **Decision:** what the project chooses to do given findings and constraints.
- **Rule:** a project-specific constraint that future work must obey.

Do not silently promote an inference into any of these.

## 3. Stage lifecycle

Use an explicit lifecycle when tracking stages:

```text
DRAFT
  ↓
RESEARCH_REQUIRED ──► RESEARCH_DONE ──┐   (evidence gap; may recur at any point)
                                      ↓
                            PREFLIGHT_VERIFIED
                                      ↓
                                    READY
                                      ↓
                                  DISPATCHED
                                      ↓
                                EXECUTOR_DONE
                                      ↓
                                  VERIFYING
                                      ├── REJECTED → READY / DISPATCHED
                                      ├── BLOCKED  → RESEARCH_REQUIRED / decision
                                      └── VERIFIED → CLOSED
```

Every transition out of `VERIFYING` passes through the orchestrator review before anything else is dispatched.

`EXECUTOR_DONE` does **not** mean the stage is complete. Only independently verified work may become `VERIFIED` or `CLOSED`.

Downstream work must not rely on an unverified upstream conclusion as settled fact.

### `SUPERSEDED` and `INVALIDATED` are not footnotes

New evidence — from research, from an implementation report, or from verification — can contradict the assumption a not-yet-dispatched stage was built on.

When that happens the orchestrator must mark the affected stages `INVALIDATED` (the premise is gone) or `SUPERSEDED` (a later stage replaces it), and re-derive the dependency direction. **Do not keep a stale task brief alive to preserve the original plan.** A brief whose premise has been overturned is more dangerous than no brief, because it still reads as approved work.

## 4. Splitting work — the ladder

Apply these checks in order. Stop at the first one that requires action.

1. **Is the ruler broken?** If the verification mechanism is unreliable, fix or isolate it before measuring new work.
2. **Is the work blocked on a decision or missing oracle?** Split the research/decision out. Do not dispatch work that has no credible acceptance mechanism.
3. **Convergent before divergent.** Prefer work that reduces uncertainty and closes known gaps before opening new subsystems or design spaces.
4. **Foundation before consumer.** If several upcoming tasks depend on the same broken primitive, stabilize that primitive as its own stage.
5. **One reviewable outcome.** If acceptance requires two independent verdicts, create two stages.
6. **Never bundle a decision with its implementation.** Determine A/B/C first; implement the accepted decision in a later stage.

A stage is appropriately sized when its acceptance checklist is binary-decidable. If that cannot be written, create a research stage first.

The orchestrator optimizes for **uncertainty reduction and verified progress**, not lines of code or task throughput.

## 5. Dependency-aware dispatch

Before dispatching a stage, determine:

- what it depends on;
- what it blocks;
- whether every dependency is verified;
- whether a decision is still open;
- whether the acceptance oracle exists;
- which role should execute it.

Prefer a dependency graph over a flat TODO list for multi-stage work.

Example:

```text
LEGACY-01 behavior mapping ─┐
                            ├→ ARCH-03 runtime boundary → IMPL-05 implementation
PROTO-02 protocol evidence ─┘                              ↓
                                                        VERIFY-06 verification
```

Do not dispatch a downstream implementation merely because an upstream executor reported success.

## 6. Pre-flight before writing a brief

Do not put unverified facts, counts, architecture claims, or legacy behavior into a task brief.

Before dispatch:

1. Read the actual relevant files.
2. Inspect call sites and behavior, not names alone.
3. Run actual counts or queries for numbers that matter.
4. Record evidence with stable identity where practical: commit/ref + file + symbol + line range.
5. Identify unknowns and label them as unknowns.
6. State in the brief that the executor must re-verify the supplied pre-flight facts.

A true local fact can still produce a wrong conclusion when the premise set is incomplete.

## 7. Task brief contract

A task brief should contain:

| Section | Required content |
|---|---|
| **§0 Before you start** | Required reading, project rules, working directory, read/write limits |
| **§1 Scope** | Deliverables plus explicit ⛔ NOT-DOING items and why they are excluded |
| **§2 Dependencies** | Verified prerequisites, blockers, decisions, upstream evidence |
| **§3 Pre-flight facts** | Evidence-backed facts, marked **re-verify these yourself** |
| **§4 ⚠ Traps** | Task-specific failure modes and how they were discovered |
| **§5 Report contract** | Required executor report structure |
| **§6 Acceptance** | Binary-decidable acceptance checks |

The NOT-DOING list is a hard scope boundary. Give the reason for each exclusion so the executor does not interpret it as an omission.

### Handoff prompt

The brief is the specification; the handoff prompt is only the entry point.

```text
Read <brief path> and execute it in the assigned role.

Working dir: <path>
<read/write constraints>

Dependencies already verified:
<ids>

⚠ <3–4 task-specific failure risks>

Re-verify the brief's facts and numbers yourself.
Follow the report contract in <location>.
```

## 8. Return contracts

Every dispatched role ends the same way: **a report returned to the orchestrator, with evidence separated from interpretation.** That separation is the contract; the section list belongs to each role's skill and must not be duplicated here.

| Role | Returns | Shape defined in |
|---|---|---|
| **Research** | evidence, measurements, inference, unknowns, options, costs | `../research/SKILL.md` §11 |
| **Implementation** | the change, the evidence for it, and what it did not do | `../implementation/SKILL.md` §7 |
| **Verification** | one verdict — ACCEPT / REJECT / BLOCKED — and what was re-run | `../verification/SKILL.md` §11 |

Three requirements apply to all three:

1. **Verified and inferred are separate sections.** An inference must state what would turn it into a verification.
2. **Mechanical claims carry actual output** — the command, the exit status, the relevant lines. `passed`, `looks good` and `see the existing system` are not evidence.
3. **The report ends at the orchestrator.** No dispatched role selects the next piece of work, opens a new stage, or acts on its own finding outside the dispatched scope.

## 9. Independent verification

Reading the report is not verification. Re-run the load-bearing assertions, in priority order, before anything is accepted.

The procedure — what to re-run first, how to test sample independence, what an absence claim must carry, how to challenge the acceptance criteria themselves — is `../verification/SKILL.md`. Do not maintain a second, weaker copy of it here.

Two contract-level rules:

- **`EXECUTOR_DONE` is a claim; `VERIFIED` is a conclusion.** Only re-running makes the second out of the first.
- **An artifact must not be certified by whoever materially authored it** — including an orchestrator who specified it in enough detail that the executor had no judgement left.

## 10. Research role boundary

Research exists to remove the uncertainty that blocks the orchestrator, not to decide what the project does with the answer.

Dispatch research when a missing fact would change any of:

```text
decomposition        sequencing          architecture decision
acceptance criteria  risk boundary
```

Hand it: the question, why it blocks, what an adequate answer looks like, the scope it may read, and the point at which it should stop and return.

Research **must not** choose a migration strategy, fix an implementation order, build the task graph, settle the architecture, or begin implementing. Those are orchestrator decisions taken *after* reading the report — and a research session that also decides removes the only independent look at its own evidence.

A research report that concludes the question cannot be answered with available evidence is a **successful** result, provided it says what is missing and what obtaining it would cost.

The detailed behavior of that role lives in `../research/SKILL.md`.

## 11. Verification role boundary

Verification is not merely `run the tests again`.

When a dedicated Verification role exists, the orchestrator should hand it:

- the accepted requirement/decision;
- the implementation diff or artifact;
- acceptance criteria;
- known traps and risk areas;
- explicit exclusions;
- relevant regression surface.

Verification should be able to challenge both the implementation and the sufficiency of the acceptance criteria.

Do not tell Verification to reproduce Dev's reasoning as its primary method. Independence is useful precisely because Verification may find a different failure model.

The detailed behavior of that role lives in `../verification/SKILL.md`. When no separate verification session is available, the orchestrator owns acceptance verification and should follow that skill, while preserving this boundary.

## 12. Implementation role boundary

Implementation owns implementation within the brief, not project-level scope expansion or unresolved architecture decisions.

If implementation exposes a missing decision, contradictory premise, or unverifiable acceptance condition, Implementation should report the blocker rather than silently choose a convenient interpretation.

The detailed behavior of that role lives in `../implementation/SKILL.md`. Task briefs must still carry enough task-specific constraints to make implementation safe, but neither this workflow skill nor the brief should grow into a language/framework coding manual.

## 13. Detecting a missing skill

When output quality repeatedly drops in the same way, first ask whether a role/domain skill is missing rather than endlessly expanding project rules.

Signals include:

| Signal | Likely missing skill |
|---|---|
| Same review problem recurs across stages | Skill for that failure class |
| Code works but violates language/framework idiom | Language/framework skill |
| Abstraction layers repeatedly grow without need | Anti-over-engineering skill |
| Verification repeatedly misses the same failure model | Verification/testing skill |
| Implementation repeatedly misreads the same kind of implementation constraint | Implementation/domain skill |
| Entering a new technical domain | Domain skill |

A **skill** counters a reusable model tendency. A **project rule** records a project-specific constraint with provenance. Do not duplicate skill manuals into `rules.md`.

## 14. Recording and overturns

- **Overturned conclusion:** never silently delete it. Record what was previously believed, the new evidence, and where the old reasoning failed.
- **New rule:** record the incident or evidence that earned it.
- **Decision:** record rationale, rejected alternatives, evidence, and conditions that should trigger reconsideration.
- **Repeated preventable failure:** after it occurs twice, prefer an executable check that can fail mechanically over another prose reminder.

Historical evidence should be version-aware. Prefer commit/ref + file + symbol/line over a naked line number when the codebase changes frequently.

## 15. When not to use this workflow

Do not impose the full workflow on exploratory prototypes where learning speed matters more than silent-error resistance.

For work where mistakes fail immediately and comprehensively, ordinary tests may be sufficient.

This workflow is most valuable when failures can remain silent:

- behavior looks correct but is subtly wrong;
- numbers look plausible;
- tests are green but incomplete;
- migration reproduces an incorrect understanding;
- one session's stale conclusion propagates into later work.

Keep governance proportional. If documentation permanently grows faster than the engineering work it protects, simplify the scaffold.

## Boundaries

The orchestrator coordinates and accepts work; Implementation constructs the change; Verification independently challenges and verifies it.

These are **logical roles**, not necessarily permanent agents. The `implementation` and `verification` skills should plug into this contract without requiring this skill to absorb their detailed behavior.

If the orchestrator materially authors an implementation artifact, mark that artifact as requiring verification by a separate session or Verification role before acceptance.
