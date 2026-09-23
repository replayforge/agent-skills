---
name: engineering-knowledge-capture
description: Capture durable engineering lessons from coding, debugging, architecture, incidents, benchmarks, reviews, and AI-assisted development. Use when a session produces reusable knowledge worth organizing into Notion or another notes MCP.
---

# Engineering Knowledge Capture

## Related skills

This skill is part of the shared engineering workflow family:

- `../work-flow/SKILL.md` — project-level workflow constitution and cross-session contract.
- `../orchestrator/SKILL.md` — orchestration and project-state governance.
- `../research/SKILL.md` — evidence gathering before a decision.
- `../project-records/SKILL.md` — the project's own operational records, which stay in the repository.
- `../implementation/SKILL.md` — implementation-session discipline.
- `../verification/SKILL.md` — independent/adversarial verification discipline.

Knowledge capture is orthogonal to those roles: it preserves durable lessons without becoming the project task log or duplicating role instructions.

It is not a step in the workflow loop. Capture after a conclusion has been **accepted** — an overturned or unverified conclusion promoted into Knowledge is worse than none, because it leaves the project that produced it and loses the context that would have corrected it.

Use this skill when a coding, debugging, architecture, incident, benchmark, review, or AI-assisted development session produces a durable technical lesson worth preserving.

## Goal

Capture reusable engineering knowledge, not a chronological development diary.

The preferred destination is a connected note-capable MCP. If a note MCP is available, inspect the notebook structure before writing and place the note into the existing hierarchy. If no note MCP is available, create or update a Markdown note locally instead.

## Trigger conditions

Capture a note when at least one of these is true:

- A non-obvious root cause was discovered.
- A reusable invariant or architecture principle emerged.
- A measurable performance result changes future design choices.
- A recurring failure mode was identified.
- A trade-off was validated with evidence.
- An implementation invalidated a prior assumption.
- A debugging technique is likely to be reused.
- An AI coding workflow produced a reusable engineering lesson.

Do not capture routine syntax, ordinary TODOs, temporary status updates, obvious documentation facts, or unverified speculation as durable knowledge.

## Destination discovery

1. Inspect currently available tools / MCP servers for a note-capable system such as Notion, Obsidian, a filesystem notes service, or another structured knowledge store.
2. Prefer an already connected note MCP over inventing a new local storage layout.
3. If the note system exposes workspace rules, README pages, taxonomy pages, or an AI-writing contract, read them before creating or moving content.
4. Inspect the current knowledge hierarchy near the intended destination. Reuse existing topics whenever possible.
5. Do not hard-code private page IDs, workspace IDs, database IDs, or URLs into the skill.
6. If no note MCP can be used, fall back to a Markdown file under `knowledge/` in the current repository or workspace.

## Notion-specific routing

When Notion MCP is available:

1. Search for a top-level Knowledge area and fetch it.
2. Read its README / rules page if one exists.
3. Read any workspace-wide AI organization rules if discoverable.
4. Search under Knowledge for an existing topic that semantically matches the note.
5. Reuse the existing topic if it is a clear fit.
6. If no suitable topic exists, create one directly under Knowledge. Avoid deep trees; prefer at most `Knowledge -> Topic -> Note` unless the existing workspace already uses a different valid pattern.
7. Create the note as a child of the selected topic.
8. Preserve the workspace's naming conventions and hierarchy instead of imposing this skill's examples.

Example routing:

```text
Knowledge
└── Distributed Systems
    └── Persist data before coverage metadata
```

or:

```text
Knowledge
└── Rust
    └── Avoid allocator pressure on latency-sensitive hot paths
```

## Markdown-first note construction

Compose the note in Markdown before persisting it through the note MCP. The Markdown is the canonical draft and should be structurally complete before write operations begin.

Use this default structure unless the notebook's local rules specify something better:

```markdown
# <descriptive title>

## Problem
What problem or failure mode was encountered?

## Context
What system, workload, or constraint made this relevant?

## Observation
What was directly observed? Separate facts from interpretation.

## Root Cause
Why did it happen?

## Key Insight
What is the durable understanding?

## Reusable Rule
State the rule in a form that can guide future engineering decisions.

## Evidence
Tests, benchmarks, logs, code paths, incidents, measurements, or source links.

## Trade-offs
What does this approach cost or give up?

## Applies When
Conditions where the rule is likely valid.

## Does Not Apply When
Boundaries, counterexamples, or cases where the rule should not be generalized.

## Checklist
- Concrete checks to reuse next time.

## Source
Commit, PR, issue, benchmark, project page, incident log, or original note when available.
```

The exact headings may be reduced for a small note, but keep the distinction between observation, interpretation, reusable rule, evidence, and scope.

## Classification rules

Before writing, classify the material:

- **Knowledge**: reusable across projects or future decisions.
- **Project record**: what happened in one project or task.
- **Source evidence**: raw benchmark, log, incident, commit, or transcript.
- **Research**: external paper or literature analysis.
- **AI workflow**: reusable prompt, agent procedure, or tool-operating pattern.

Only durable conclusions belong in Knowledge. Keep source material in its original system and link back to it where possible.

## Duplicate handling

Before creating a new note:

1. Search for the same concept and nearby synonyms.
2. If an existing note already captures the same rule, update or append evidence instead of creating a duplicate.
3. If the new result contradicts an existing note, do not silently overwrite it. Record the conflicting evidence and adjust confidence / scope.
4. If two notes overlap but cover meaningfully different contexts, keep both and cross-link them.

## Evidence and confidence

Prefer evidence-backed conclusions.

- **Confirmed**: supported by tests, reproducible benchmark, production behavior, or primary documentation.
- **Likely**: strong engineering inference but not fully validated.
- **Experimental**: hypothesis or early observation.

Do not present likely or experimental conclusions as universal rules.

## Safety and privacy

Never persist secrets, credentials, API keys, private keys, seed phrases, access tokens, passwords, recovery codes, or other sensitive values into ordinary knowledge notes.

If a source contains sensitive data, preserve only the reusable technical pattern and omit the secret value. Do not echo secret-looking strings in the final summary.

## Write behavior

- Read before write.
- Make the smallest complete change.
- Reuse the existing notebook hierarchy.
- Prefer updating an existing note over spawning near-duplicates.
- Do not reorganize unrelated pages while capturing one insight.
- Do not create a topic merely because one can be created; create it only when no existing topic is a clear fit.
- Keep titles independently understandable.

## Completion report

After writing, report briefly:

- what durable insight was captured;
- whether an existing note was updated or a new note was created;
- where it was stored;
- any uncertainty or evidence still missing.

Do not dump the full development session into the report.
