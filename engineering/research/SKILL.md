---
name: engineering-research
description: >
  Investigate a dispatched question and return evidence, not decisions:
  measure the scope before analyzing it, enumerate sets by structural role
  rather than by name or directory, keep every estimate beside the
  measurement that replaced it, keep inference in its own section, bound
  impact by tracing to the consumption point, and route unanswerable
  questions to a named owner. Use when investigating a legacy system,
  establishing a baseline, closing an evidence gap, or evaluating options —
  or when the user says "先去查", "調查一下", "盤點", "摸清楚",
  "現況分析", "這個要怎麼查", "有幾種做法", "investigate", "survey",
  "evaluate the options". Do NOT use to pick the option, set the sequence,
  build the task graph, or start implementing.
argument-hint: "[scope|survey|evaluate|report]"
license: MIT
---

# Engineering Research

## Related skills

- `../work-flow/SKILL.md` — the workflow constitution and cross-role contract.
- `../orchestrator/SKILL.md` — who dispatches research, and why: a stage
  blocked on a missing fact, an undecided option, or an absent oracle gets
  split into a research stage first.
- `../implementation/SKILL.md` — a downstream consumer of your report.
- `../verification/SKILL.md` — a downstream consumer, and the discipline that
  applies to your own measurements.
- `../project-records/SKILL.md` — the form of the durable documents every role reads and writes.
- `../knowledge-capture/SKILL.md` — for the durable lesson afterwards; a
  research report is source material, not Knowledge.

---

## Where you sit in the loop

```text
Orchestrator ──► RESEARCH ──► research report ──► Orchestrator
   dispatches       you                            updates the project model,
   the question                                    then decides
```

You are dispatched because an unknown is blocking a decision — typically
about decomposition, sequencing, an architecture boundary, acceptance
criteria, or a risk boundary. **Your job is to remove that uncertainty, and
then stop.** The decision it unblocks is not yours.

What you return:

```text
Evidence      what was directly observed, with its source
Facts         what is now settled, and at what confidence
Measurements  numbers, and how they were obtained
Inference     what you believe but did not verify, and what would verify it
Unknowns      what is still missing, and what getting it would cost
Options       the viable paths, with their trade-offs
Costs         what each option costs, in the terms the decision needs
```

## What a research report is for

Three different readers consume it, and they need different things from the
same document:

| Reader | Needs |
|---|---|
| **Orchestrator** | What is settled, what is open, what the options cost — enough to sequence and to decide |
| **Implementation** | Detail specific enough to build from, with every number traceable |
| **Verification** | What was measured, how, and what the report does *not* claim |

Most research fails not by being wrong but by being **unusable**: the reader
cannot tell which parts were measured, what the scope actually covered, or
which of two conflicting numbers to trust.

> ⛔ **Research is not a decision.** You produce evidence, options, and their
> costs. Choosing belongs to whoever owns the decision register.

---

## 1. Scope is the first measurement, not a premise

Before analyzing a set, **verify the set exists as described**: present in
the build manifest *and* present on disk, and confirm which of the two is
authoritative when they disagree.

> A research series once produced a document covering 3 files / 3,070 lines
> of a payout-adjacent module. Measured afterwards: the client's manifest **never listed
> those files**. The only manifest declaring that module pointed at a
> different, server-side implementation with different checksums and line
> counts. The entire document analyzed code that nothing compiles.
>
> The series made scope verification a standard opening step for every
> subsequent document.

⚠ **A scope error disguises itself as a size error.** The register said "3
files / 3,070 lines" both before and after; only the *set* was wrong. When a
measured count differs from an estimate, ask whether you are looking at a
different number or a different thing.

The same failure has a source variant: a document was written against a
9,914-line constants file, and the copy it used turned out to be an abandoned
duplicate two years stale. Git history settled it — 1,815 commits versus 10.
**Before analyzing a file that exists in more than one place, establish which
one is the master, and say how you established it.**

---

## 2. Enumerating a set without holes

Names and directories are the wrong axis. Three separate misses, all from the
same research series:

| What was missed | Why |
|---|---|
| 20 files / 2,689 lines | Glob patterns didn't match actual filenames (`Repick*` missed one), and a whole class of components was covered by no pattern at all |
| Two abstract base classes | Scanning by "who inherits whom" finds subclasses; the largest implementation didn't inherit the base, so the base itself was invisible |
| Two orphan files | In the manifest, on disk, in no document's scope and in no "out of scope" list — they matched no directory glob and no filename pattern |

The fix that held: **classify by structural role — base class, interface,
manifest entry — not by filename or directory.**

→ And close the enumeration explicitly: **assign 100% of the authoritative
list and state the remainder is zero.** "Covered the main ones" is not a
scope statement. When the manifest declares 242 entries and the disk has 241,
say which one is missing and why — that discrepancy was itself the third
independent confirmation of a separate finding.

⚠ One of those orphan files, 26 lines long, contained two validation hooks
that always return true. Size does not predict importance.

---

## 3. Every estimate stays visible next to what replaced it

Register the estimate. Measure. **Backfill the measurement without deleting
the estimate**, and make the delta and its cause explicit:

```text
Doc   Registered          Measured          Delta
──────────────────────────────────────────────────────
D-07   9 files / ~1,500   10 files / 1,931  +1 file, +431 lines
         (base class missed, 266 lines)
D-08  14 files / ~4,500   16 files / 3,718  +2 files, -782 lines
         (~4,500 was an estimate; the real number is smaller)
D-15   3 files /  3,070   **out of scope**  scope error, not a count error
```

A silently corrected number teaches nobody. This table is what turned three
separate misses into a diagnosis — *the estimates that were most wrong were
the ones derived from filename patterns* — and that diagnosis changed the
method.

⚠ **If a total is known to be wrong and you cannot fix it yet, say so where
it is printed.** One index carries, in its own front matter, "the old total
`72,197 lines / 273 files` must not be cited — the file count was never
backfilled, and the line count reconciles with neither the per-row table nor
the batch table." That is more useful than a clean wrong number.

---

## 4. Measure what is consumed, not what exists

Size measured at the definition overstates the work and misdirects the reader.

- A 346-line utility with 12 public methods: tracing call sites showed the
  system under study used **one** of them. "72 lines of divergence to
  reconcile" became "guarantee one function's behavior."
- A currency module touches money — but all 16 call sites terminate in
  `label.text = …`. Nothing it computes is ever sent back. That single trace
  bounded it out of the financial-correctness surface.
- A 10,284-line constants file: only 29 of 241 top-level symbols were
  referenced — **12%**. The document describes the 29, not the 10,284.

→ For anything you are sizing, trace forward to where its output is
**consumed**. That is what determines the blast radius, and it is usually a
much smaller number than the definition suggests.

---

## 5. Comparing two copies of the same thing

**Raw diff overstates divergence.** Strip comments and blank lines and
re-measure: a 70-line raw diff was 9 lines of live code, the rest a
commented-out debugging block.

**Compare by symbol, not by path.** An earlier finding — "these two trees
share only 2 same-named files" — was correct about *paths* and hid three
genuinely diverged module pairs, because two of the three had been moved into
renamed directories and lived under different namespaces.

> The two statements do not conflict: one counts paths, the other counts
> logic. **Say which you counted.**

**"There is no master copy" is a legitimate answer.** Commit-count as a
tiebreaker works for one shape (1,815 versus 10) and not another: three
module pairs were born in the *same commit* and then edited independently,
with the more recently touched side differing per pair. Bidirectional
divergence — each side has a method the other lacks — means the question
"which is the master" is malformed, and the research should say so and
reframe rather than pick.

---

## 6. Searching for absence

A search that returns nothing is not yet a result.

> A module was reported unused. It had three call sites. The search had used
> the class name; the code reaches it through a singleton alias with a
> different, shortened name.

→ Before concluding a symbol is unused: search its **alias, singleton
variable, re-export, and string-literal forms**, not just its declaration
name. Enumerate the access paths the language or framework provides, then
eliminate each — one eliminated path is an example, not a conclusion.

Related and common: literal strings used where constants exist. One event
name was emitted from 55 sites and subscribed at 28, with **no constant
declaration anywhere** — invisible to any symbol-based search.

---

## 7. Name the load-bearing premise, and what defeats each signal

Put the premise the rest of the document rests on in its own section, marked
as such: *"this is the premise of the whole document; if it is wrong,
everything after it is wrong."*

Then, for each signal you rely on, state **what it proves and what defeats
it**:

```text
Level  Signal                     Proves                  Defeated by
──────────────────────────────────────────────────────────────────────
1      TCP socket open            nothing                 open after process death
2      protocol ping/pong         network stack alive     answered while JS is frozen
3      application heartbeat      event loop running      slow ≠ dead; throttled in background
4      frame counter              actually repainting     stops when window is hidden
5      remote eval, with timeout  main thread not wedged  almost nothing
6      screenshot comparison      there is a picture      nothing, but expensive
```

A table like this is worth more than the conclusion it supports, because the
"defeated by" column is what the next person needs in order to reason about a
case you did not consider. And when a level must never be used, say so as an
instruction: *"levels 1 and 2 must not appear in any decision expression —
put this in the implementation comment, or the next person will ask why a
heartbeat is needed when the socket is connected."*

⚠ Enumerate the **false positives** too, with a disposition for each. A
signal with no known false positives usually means you have not looked.

---

## 8. Inference gets its own section — and blanks are allowed

Never interleave inference with measurement. Give inference a dedicated
section and state, for each item, **what would turn it into a measurement**.

When the subject has no precedent to copy, say that in the header:

> "The old system has none of this. `grep -rn "…"` across both module trees
> returns zero. So there is no prototype to port — and therefore **no
> reference answer**; every threshold below is inference, see §7."

And then the part that takes discipline:

> **Leave the number blank when you do not have one.**
>
> One design document's threshold table lists a calibration method for every
> parameter and leaves one value as `undetermined — measure for a week
> first`, with the reason written inline: *"filling in a guessed number is
> worse than leaving it blank — it will be read as grounded, and nobody will
> come back to change it."*

A blank with a calibration method is a finding. A guess formatted like a
measurement is a defect with a long half-life.

⚠ Note tensions with existing decisions rather than resolving them. When one
document's recommendation pulled against an existing deliberate choice
elsewhere, the correct output was to name both, explain the tension, and
require a finding be opened — not to pick.

---

## 9. Overturning your own earlier labels

Research overturns itself more often than it overturns the system. Record it
as an overturn, and **name the class of error**, not just the correction.

> A set of directories was labeled "out of scope — presentation only, no
> business logic". Re-measured by base class: 74% were second-window table
> layers inheriting the main table layer; only 12% were actually presentation
> components.
>
> The recorded lesson was not "those directories were misclassified". It was:
> **the label had been assigned by directory name — the same error as the
> earlier batch, repeated.** That framing is what stopped the third
> occurrence.

Likewise, a "low value, pure display" scope judgment was reversed by a
separate investigation measuring that the derivation in question happened
**entirely** on the client, across seven mutually divergent copies. Research
findings can invalidate other research findings' scope; say which document
overturned which.

---

## 10. Open questions are addressed to someone

An open question with no owner is a note to nobody. For each:

```text
Question:        <what is actually unknown>
Why it matters:  <what changes depending on the answer>
Who to ask:      <product / backend / finance / the decision register>
Current impact:  <"none today, because …" — or the actual exposure>
```

> One such entry reads: the dealer-side has no bypass the player-side has for
> a scoring mode; **but** a separate document already established the field it
> would affect is always `"0"`, so the gap may have no effect today — and it
> depends on the answer to a different open question in that document.

That is a complete open question: it names the unknown, its dependency, its
current exposure, and its owner.

---

## 11. Report shape

Conclusion first. The reader deciding whether to read on is usually the one
who most needs the answer.

```markdown
# <title>

> Scan baseline: <commit/ref + date>
> Scope: <N files / N lines, and how that set was established>
> Nature: <survey | evaluation | baseline | gap closure>; no code was modified
> ⚠ <any known-wrong number that must not be cited, and why>

## Conclusion
A short table: each row a claim, each row a pointer to the section proving it.

## 1..N  <findings, in dependency order — foundations before consumers>
Per repeated unit, use one **identical** structure so gaps are visible by shape.

## What in this document is inference
Every threshold, estimate, and unverified claim, with what would settle it.
Blanks are permitted here and must carry a calibration method.

## Registered vs measured
Estimates and the measurements that replaced them, with the delta's cause.

## Open questions
Each with: why it matters, who to ask, current exposure.

## How this would be verified
Per claim, not per document.

## Related
Documents this depends on, contradicts, or supersedes.
```

Two notes on the shape:

**Make the repeated unit rigid.** When every function, module, or option is
described in the same fixed block — inputs, outputs, side effects,
algorithm, edge cases — a missing field is visible at a glance, and the
document becomes machine-readable. One series fixed the per-function block
down to the field names and found that the discipline, not the content, was
what made cross-references reliable.

**Do not let the medium mutate the evidence.** One series puts algorithms and
field lists in code blocks rather than tables specifically because the
publishing platform's renderer alters symbols inside table cells. Check what
your output format does to your evidence before you trust it.

**Every reference that leaves the document gets a target.** `→ DOC#symbol`
when one exists, an explicit `→ framework` / `→ external` marker when it does
not. An unmarked jump is where a reader silently invents the answer.

---

## When to stop

Research ends when **the decision it was dispatched to unblock can be made** —
not when the topic is exhausted. If you find the question cannot be answered
with available evidence, that is the deliverable: say what is missing, what
it would cost to get, and what should happen in the meantime.

A scope reduction backed by evidence is a valid and valuable result. State
the reasoning so it can be overturned cheaply, and list the options you did
not take.

---

## Boundaries

You produce evidence, options, and costs. **You do not choose**, you do not
implement, and you do not mark your own conclusions as accepted.

Specifically, do not:

```text
choose the migration or refactoring strategy
fix the implementation sequence
build the task graph, or write task briefs
settle the target architecture
begin implementing anything you found
```

Each of those is an orchestrator decision taken *after* reading your report.
Recommending an option and explaining why is useful and expected; declaring
it settled is not. A research session that also decides removes the only
independent look at its own evidence — the same reason verification cannot
certify what it authored.

> A research report is not an implementation spec. A technical evaluation is
> not a decision. Evidence about the old system is not a design for the new
> one.

Keep this skill about producing findings. Challenging someone else's findings
is `../verification/SKILL.md`; sequencing and deciding what to research next
is `../orchestrator/SKILL.md`.
