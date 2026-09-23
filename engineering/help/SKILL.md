---
name: engineering-help
description: >
  Entry point for the engineering skill family: which of the seven skills to
  load for the situation at hand, how they hand work to each other, and what
  each one refuses to do. Use when the user asks what skills are available,
  which one applies, how this workflow runs, or says "有哪些 skill",
  "這套怎麼用", "我該用哪個", "engineering help", "list the skills".
  Also use when a session is about to act in a role and the role is ambiguous.
license: MIT
---

# Engineering Skills — which one, when

Seven skills. **One constitution, five roles, one about the documents.**

## Pick by what you are about to do

| You are about to… | Load |
|---|---|
| Decide what happens next; split work; write a brief; accept a result | `engineering-orchestrator` |
| Find something out so a decision can be made | `engineering-research` |
| Build the thing one brief asks for | `engineering-implementation` |
| Challenge somebody else's result | `engineering-verification` |
| Write or fix a document another session will read | `engineering-project-records` |
| Preserve a lesson outside this project | `engineering-knowledge-capture` |
| Understand how the roles fit together | `engineering-work-flow` |

**Load `engineering-work-flow` alongside whichever role applies.** It is the
contract between roles, not a substitute for any of them.

## The loop

```text
              ┌─────────────────────────────────────────┐
              │                                         │
   ORCHESTRATOR REVIEW ◄─────────────────────────────┐  │
     │  the only decision point                      │  │
     ├── evidence gap ──► RESEARCH ──► report ───────┤  │
     ├── task brief ────► IMPLEMENTATION             │  │
     │                        └─► VERIFICATION ──────┘  │
     └── nothing unblocked remains ──► done             │
              └─────────────────────────────────────────┘
```

Research, Implementation and Verification each end by **returning a report
and stopping**. Verification is never the endpoint — every verdict re-enters
the review. Research is re-enterable at every review, not only at the start.

## What each one refuses to do

| Role | Will not |
|---|---|
| Orchestrator | Implement. Certify what it materially authored. |
| Research | Choose the option, set the sequence, build the task graph, start implementing. |
| Implementation | Expand scope. Settle an open decision. Self-certify. |
| Verification | Verify what it authored. Fix what it found. Pick the next task. |

If you find yourself about to do something on that list, you are in the
wrong role — stop and hand it back.

## When not to use any of this

Exploratory prototypes, and anything where a mistake fails immediately and
loudly. This family defends against **silent** errors: the screen looks
right, the numbers look reasonable, the checks are green, and it is wrong.

Keep the apparatus proportional. If the documents grow faster than the work
they protect, delete rather than add.

## Install

```bash
./install.sh --list       # what would be linked, changes nothing
./install.sh              # symlink into ~/.claude/skills and ~/.agents/skills
./install.sh --uninstall  # remove only the links pointing at this repo
```

Symlinks, not copies — `git pull` updates every install at once.
