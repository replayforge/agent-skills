# agent-skills

Reusable agent skills for engineering workflows.

## Skills

### engineering/

Engineering-oriented skills are grouped under a shared namespace. The workflow is intentionally separated from role behavior and durable knowledge capture so each layer can evolve independently.

```text
engineering/
├── work-flow/
├── knowledge-capture/
├── orchestrator/        # planned
├── implementation/      # planned
└── verification/        # planned
```

#### engineering/work-flow

Defines the project-level AI engineering workflow: multi-stage task briefs, cross-session verification, persistent project state, evidence discipline, stage lifecycle, and role boundaries. This is the workflow constitution: it defines how Human, Orchestrator, Implementation, and Verification interact without absorbing each role's detailed behavior.

#### engineering/knowledge-capture

Captures durable engineering lessons from coding, debugging, architecture, benchmarks, incidents, and reviews. It discovers an available note-capable MCP, inspects the notebook hierarchy before writing, composes the note as Markdown, and routes it into the existing knowledge structure instead of dumping session logs.

The skill is designed to work especially well with Notion MCP, but it does not hard-code a private workspace ID or page URL. It discovers the current Knowledge root, reads nearby workspace rules, reuses an existing topic when possible, and only creates a topic when the notebook structure actually needs one.

#### engineering/orchestrator — planned

Owns decomposition, dependency-aware stage selection, pre-flight, task briefs, dispatch, acceptance decisions, overturn handling, and project-state governance. It coordinates work but must not independently certify artifacts it materially authored.

#### engineering/implementation — planned

Owns the implementation session: re-verifying brief premises, making the smallest in-scope change, respecting NOT-DOING boundaries, escalating missing decisions instead of inventing them, running mechanical checks, and returning an evidence-backed result report.

#### engineering/verification — planned

Owns independent and adversarial verification: challenging implementation behavior, acceptance criteria, regression surface, evidence quality, sample independence, and silent-error risks. It must not merely reproduce the implementation session's reasoning.

## Role model

```text
Human
  ↓ scope / priority / decisions
Orchestrator
  ↓ task contract
Implementation
  ↓ artifact + evidence
Verification
  ↓ accept / reject evidence
Orchestrator
  ↓ update project state / next stage
```

These are logical roles. Separate sessions are preferred when independence matters.

## Zed

Zed loads skills from `~/.agents/skills/` globally or `<worktree>/.agents/skills/` per project. Copy or symlink the desired skill folder into one of those locations.

Zed can also import a skill from a GitHub Markdown URL with the command palette action `agent: create skill from url`. For example, import `engineering/knowledge-capture/SKILL.md` or `engineering/work-flow/SKILL.md`.

## Design rules

- Workflow, role, domain, and knowledge-capture concerns remain separable.
- `work-flow` defines the cross-role contract; role skills define role-specific behavior.
- Implementation does not silently make unresolved project-level decisions.
- Verification remains independent from material authorship.
- Knowledge is not a development diary.
- Raw logs, benchmarks, incidents, and project history stay as source material; only reusable conclusions become Knowledge.
- Existing notebook information architecture wins over assumptions in the skill.
- Do not create a new category for every note.
- Never persist secrets, credentials, private keys, seed phrases, or tokens into ordinary knowledge notes.
