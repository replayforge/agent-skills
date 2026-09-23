# agent-skills

Reusable agent skills for engineering workflows.

## Skills

### engineering/

Engineering-oriented skills are grouped under a shared namespace. The workflow is intentionally separated from role behavior and durable knowledge capture so each layer can evolve independently.

```text
engineering/
├── work-flow/
├── knowledge-capture/
├── research/
├── implementation/
├── verification/
├── orchestrator/
└── project-records/
```

#### engineering/work-flow

Defines the project-level AI engineering workflow: multi-stage task briefs, cross-session verification, persistent project state, evidence discipline, stage lifecycle, and role boundaries. This is the workflow constitution: it defines how Human, Orchestrator, Implementation, and Verification interact without absorbing each role's detailed behavior.

#### engineering/knowledge-capture

Captures durable engineering lessons from coding, debugging, architecture, benchmarks, incidents, and reviews. It discovers an available note-capable MCP, inspects the notebook hierarchy before writing, composes the note as Markdown, and routes it into the existing knowledge structure instead of dumping session logs.

The skill is designed to work especially well with Notion MCP, but it does not hard-code a private workspace ID or page URL. It discovers the current Knowledge root, reads nearby workspace rules, reuses an existing topic when possible, and only creates a topic when the notebook structure actually needs one.

#### engineering/research

Owns the investigation dispatched when a stage is blocked on a missing fact, an undecided option, or an absent oracle: establishing and measuring the scope before analyzing it, enumerating sets by structural role rather than by name or directory, keeping every estimate visible beside the measurement that replaced it, bounding impact by tracing to the consumption point, and routing unanswerable questions to a named owner.

Its central discipline is that measurement and inference never share a section, and that a blank with a calibration method beats a guess formatted like a measurement.

#### engineering/implementation

Owns the implementation session: re-verifying the brief's premises before trusting them, establishing facts from call sites rather than names, fixing at the layer all callers converge on, escalating open decisions instead of settling them, keeping a provisional path loud rather than silently half-correct, and returning a report that separates verified fact from inference with pasted command output.

Each invariant is derived from a real incident in which a session reasoned validly from a true premise and still shipped a wrong result.

#### engineering/verification

Owns independent and adversarial verification: re-running the load-bearing assertions rather than reading the report, refusing green that was obtained by rerunning, checking whether repeated samples are actually independent, requiring the previous version's number beside every improved metric, demanding an enumeration behind every absence claim, and challenging the acceptance criteria themselves.

It deliberately does not reproduce the implementation session's reasoning — following the same path reaches the same place.

#### engineering/orchestrator

Owns decomposition, dependency-aware stage selection, pre-flight, task briefs, dispatch, acceptance decisions, overturn handling, and project-state governance. It coordinates work but must not independently certify artifacts it materially authored.

It deliberately does not restate the constitution. What it adds is the coordinating role's own judgment: which lever catches which failure mode, why briefs are the usual point of failure (with the orchestrator's own errors as the evidence), when to raise a missing skill rather than rewrite an instruction, and when a written reminder should be promoted into a mechanical check.

#### engineering/project-records

Owns the form of the durable markdown that crosses sessions: stable ID schemes that double as search keys, append-only ordering, scannable index tables, closed status vocabularies, keeping overturned conclusions without misleading the next reader, placing a warning at every point a search can land on the thing it protects, and putting a mechanical check on the parts that rot.

It assumes the reader is another role, in another session, with no context, arriving by `grep` — not someone reading the file top to bottom.

## Role model

```text
Human
  │  scope / priority / decisions
  ▼
ORCHESTRATOR REVIEW  ◄──────────────────────────────────────┐
  owns the project model, task graph and sequencing         │
  │                                                         │
  ├── evidence gap ──► Research ──► evidence + options ──────┤
  │                                                         │
  ├── task brief ────► Implementation ──► artifact + evidence
  │                                            │            │
  │                                            ▼            │
  │                                      Verification       │
  │                                            │            │
  │                              ACCEPT / REJECT / BLOCKED ──┘
  │
  └── nothing unblocked remains ──► done
```

These are logical roles. Separate sessions are preferred when independence matters.

The loop is the point. The orchestrator is the **only** decision point: Research, Implementation and Verification each end by returning a report and stop there. Verification is never the endpoint — every verdict re-enters the review, where the project model is updated, stale stages are invalidated, and the next move is chosen. Research is re-enterable at every review, not only at the start.

Decomposition is progressive: split only as far as current evidence supports, keep distant work coarse, and refine a band only once the boundary it depends on has been verified.

## Zed

Zed loads skills from `~/.agents/skills/` globally or `<worktree>/.agents/skills/` per project. Copy or symlink the desired skill folder into one of those locations.

Zed can also import a skill from a GitHub Markdown URL with the command palette action `agent: create skill from url`. For example, import `engineering/knowledge-capture/SKILL.md` or `engineering/work-flow/SKILL.md`.

A session normally loads `work-flow` plus the one role skill it is acting as. Loading all four at once is possible but dilutes the role boundary that makes the split useful.

## Design rules

- Workflow, role, domain, and knowledge-capture concerns remain separable.
- `work-flow` defines the cross-role contract; role skills define role-specific behavior and must not restate it.
- A role skill states the invariants it does **not** own and points at the sibling that does. The same historical failure may appear in two skills, but never as the same invariant: `implementation` constrains how a claim is produced, `verification` how one is accepted.
- The orchestrator is the only decision point; every dispatched role returns a report and stops.
- Decomposition depth is bounded by evidence, and an initial decomposition is a hypothesis.
- Research produces evidence, options, and costs; it does not choose.
- Implementation does not silently make unresolved project-level decisions.
- Verification remains independent from material authorship.
- Project records are the project's own operational state and stay in the repository; Knowledge is what leaves it.
- Anything that must be findable by a role other than its author needs an ID.
- Knowledge is not a development diary.
- Raw logs, benchmarks, incidents, and project history stay as source material; only reusable conclusions become Knowledge.
- Existing notebook information architecture wins over assumptions in the skill.
- Do not create a new category for every note.
- Never persist secrets, credentials, private keys, seed phrases, or tokens into ordinary knowledge notes.
