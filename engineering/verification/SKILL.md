---
name: engineering-verification
description: >
  Independently challenge someone else's result: re-run the load-bearing
  assertions instead of reading the report, refuse green that was obtained by
  rerunning, test whether repeated samples are actually independent, demand
  the previous value beside every improved metric, require an enumeration
  behind every absence claim, distrust any finding whose search key was a
  name rather than the thing itself, and challenge the acceptance criteria
  themselves. Returns one verdict — ACCEPT / REJECT / BLOCKED — to the
  orchestrator. Use when reviewing, auditing or accepting a result report,
  diff, benchmark or acceptance run, or when the user says "驗證", "驗收",
  "複查", "幫我確認", "這份報告可信嗎", "這個真的跑過嗎", "挑戰這個結論",
  "verify this", "challenge this", "is this actually green". Do NOT use to
  verify work you materially authored, and do not fix what you find.
argument-hint: "[accept|challenge|audit]"
license: MIT
---

# Engineering Verification

## Related skills

- `../work-flow/SKILL.md` — the workflow constitution and cross-role contract.
- `../implementation/SKILL.md` — how a change and its evidence are *produced*;
  this file constrains how they are *accepted*.
- `../orchestrator/SKILL.md` — decomposition, dispatch, acceptance.
- `../research/SKILL.md` — evidence gathering dispatched before a decision or implementation can proceed.
- `../project-records/SKILL.md` — the form of the durable documents every role reads and writes.
- `../knowledge-capture/SKILL.md` — durable knowledge extraction.

## The core invariant

**Reports are claims. Evidence is verification.**

Detail is not evidence. Plausibility is not evidence. "Tests passed" is not
evidence. A report that is thorough, well-structured, and internally
consistent is exactly the kind that has historically been wrong — because
the author was careful, and carefulness produces confident prose regardless
of whether the premise set was complete.

Your job is **not** to re-derive the implementer's reasoning. If you follow
the same path you will reach the same place. Independence is useful
precisely because you may find a *different* failure model.

---

## 1. What to re-run, in order

Reading the report is not verification. Re-run the load-bearing assertions
yourself, in this priority:

1. **Anything that contradicts the brief or prior verified state.** Highest
   information density in the whole report — one of the two is wrong, and
   either answer is valuable.
2. **Claims with no file:line** — or with a file:line that does not say
   which branch it belongs to (§5).
3. **Numbers that gate a decision.** An estimate written in the same tone as
   a measurement is still an estimate. In the reference project "each of the
   other variants is 2–4× the work" drove sequencing for a round; measured
   overlap was 60–95%, and one variant had two new nodes.
4. **"All green" claims.** Run them.
5. **Changes to shared foundations** that multiple downstream stages will
   build on before anyone looks again.

---

## 2. Green that came from a rerun is not green

If a check fails and then passes on the same code, the failure is **data**,
not noise.

> A pixel-comparison harness disagreed with itself; the response was to warm
> it up and rerun, and the second result was written into the report as the
> evidence. The real cause — the capture tool did not wait for asynchronously
> opened overlays, affecting 15 of 51 URLs — took two more rounds to surface.

Ask of every acceptance run:

- How many times was this executed, and what happened on the other runs?
- Were the failing runs kept in the report, or replaced?
- Was there a code or harness change between the failure and the pass? If
  not, the pass measured flake, not correctness.

**A check that misfires trains people to ignore it** — and it will then be
ignored on the day it is right. A flaky ruler is a blocking defect in its own
right, ahead of whatever it was supposed to measure.

---

## 3. Are the samples independent?

A fixed-baseline pairwise comparison is not N independent samples.

```
1 vs 2   differ      ← reported as "four failures"
1 vs 3   differ
1 vs 4   differ
1 vs 5   differ

2 vs 3   identical   ← runs 2–5 all agree
2 vs 4   identical      run 1 was the sole outlier
…
```

One event, counted four times. The conclusion built on that count ("stably
unstable") overturned a conclusion that was in fact correct.

→ Three checks, all cheap:

1. **Compare all pairs, or look at the distribution of values directly** —
   hash counts, histograms — not just "does it match the baseline".
2. **Read the shape, not the failure count.** `{73:1}` and `{20,19,18,17}`
   are different faults: the first has a single cause, only the second is
   noise. In the reference project the `{73:1}` shape by itself falsified the
   previous round's attribution to rasterizer rounding.
3. **Before accepting "stable N times", ask what those N runs shared** —
   baseline, machine, process, a single cold start. Any of those collapses N
   toward 1.

⚠ This failure mode **specifically disguises itself as having been verified**:
every instance above came with real measured data. The sampling method made
the data say something false.

---

## 4. Every improved metric needs the previous value beside it

This is the highest-yield check in this file, because the information
required to catch it was already present and still missed.

> A harness fix resolved the overlay-timing problem and, in the same change,
> degraded byte-exact stability from 50/51 to 47–49/51. **Both numbers were in
> that round's own report** — the before in §1, the after in the conclusion.
> Nobody put them on the same line. The regression survived the round.

→ When a report claims a metric improved, **require the prior version's value
rendered adjacently**, per row, in the same table. Not "in an earlier
section". Not "see the previous report".

→ And ask the complementary question: **what else does this change move?**
A fix that alters when a measurement is taken changes every measurement, not
only the one it targeted.

---

## 5. Citations

A file:line is a pointer, not a proof.

**Demand which path or branch the line belongs to.** A finding cited
`video-player.d.ts:54` as showing that the legacy system refreshed a
short-lived credential. The line existed and said what was quoted — but it
belonged to the *other* provider's event list, and the finding was about the
first provider. Actual behavior: no refresh mechanism at all. The sentence
survived three rounds, read every time, because a line number looks checked.

`video-player.d.ts:54` is not enough. `video-player.d.ts:54, which is in the
Agora event list` is — the moment it is written, "so what about the other
one?" asks itself.

⚠ Related: **"the legacy system does it this way" is a sentence downstream
readers will go looking for.** Getting it wrong doesn't merely make the
document inaccurate; it sends someone hunting for something that doesn't
exist and then doubting themselves.

---

## 6. A name is not the thing

Every search key you type is a **name** someone chose. The thing you are
looking for does not have to carry it.

> A pattern anchored on `errorType\s*==` found 7 sites and two distinct error
> codes. The population was 8 sites and **four** codes — one call site wrote
> `if (err === 210 || err === 4130)`. The variable was named `err`. The claim
> "the population is only these two values" was built on a naming accident.

Three shapes of the same mistake, all from one day of one project, all by
someone who ran real commands and read the output correctly:

| Anchored on | Claimed | Actually |
|---|---|---|
| **File names** (`find -iname "*net*"`) | "this framework has no network layer" | It had one — and it was the mount point for the entire protocol layer |
| **Name shape** ("the 6 with an underscore") | "fixing the character class recovers 6" | It recovered **1**; the other 5 were missed for a different reason. The grouping was by spelling, not by cause |
| **Variable name** (`errorType`) | "the population is 2 values" | 4 values, 8 sites |

→ **Search for the thing by its value or its structure, not by its label.**
Looking for error codes? Search the numeric literals, not the variable that
holds them. Looking for a network layer? Search `WebSocket|fetch(|XMLHttpRequest`,
not filenames containing `net`.

→ When a name *is* the only handle you have, **state it as the population
definition** — "sites where the literal `errorType` is compared", not "the
error-code sites" — so the next reader can see what the count excludes.

⚠ This one does not feel like guessing. The command ran, the output was real,
the reading was correct. The defect is upstream of all of that, in the choice
of search key.

---

## 7. Absence claims need an enumeration

"Dead code", "never called", "unreachable", "that mechanism isn't used",
"the field is unused" — for each, require the answer to:

> **How many ways does this system have to produce that behavior, and were
> all of them eliminated?**

Eliminating one path is an example, not a verification. A conclusion that
seven buttons were dead rested on one correct observation about one of the
framework's **seven** binding mechanisms. Live buttons were deliberately
broken on the strength of it.

⚠ **If the report had to invent a rationale for why the old system behaved
oddly** — "the missing close button must be a deliberate forced-input gate" —
treat that as a defect signal, not as supporting context. A story attached
to a wrong conclusion makes it more credible and much harder to overturn.

---

## 8. Generalization needs a denominator

Before accepting a stated limit ("X is unattainable across processes", "this
can't be made deterministic"), ask **how many units failed out of how many**.

One round generalized an impossibility from 1 unstable file out of 51. The
next round's warm-up pass produced 51/51.

A limit derived from a small number of failures is a hypothesis about a
mechanism. Require the mechanism, or downgrade the claim.

---

## 9. Verify the acceptance criteria, not only the result

The acceptance steps are themselves an artifact under review.

**Run every executable assertion in the acceptance document yourself.** In
the reference project two separately written acceptance steps were false the
first time anyone executed them — and one of those executions is what
uncovered that the entire development toolbar, including the mock transport,
was shipping inside the production bundle.

> ⚠ **An always-failing acceptance step is worse than no step.** QA reports a
> false failure, and the next person makes it green by changing *the thing
> being tested*.

Also ask of each criterion:

- **Is it binary-decidable?** If two readers could disagree, it isn't a
  criterion.
- **Does it test the layer that actually breaks?** A unit test asserting
  *what gets sent* cannot see a fallback that is rejected on arrival. Both
  facts were true; only one of them was the behavior.
- **What does the green light mean?** Require the tool to state what it
  proves **and what it does not prove**. A harness that produces a number
  with no declared boundary produces a green light with no semantics.
- **Is the regression surface covered**, or only the changed line?

---

## 10. The apparatus must not disturb its object

Verification tooling is under review too.

> A reproduction script restored each file it had modified with
> `git checkout`. The fix under test lived in one of those files. After the
> first iteration, every subsequent measurement ran against code with the fix
> removed — and it **looked like a result**: the first file reported "fixed",
> the second "not fixed", which reads naturally as "the fix only covers one
> path".

→ Require of any verification script: **can it answer "was the thing I just
measured the version I think it was?"** Acceptable answers: commit or stash
the change under test and only touch files that don't contain it; restore
via file copy rather than version control; print a distinguishing line before
and after every iteration.

→ Related: a textual search does not validate a resolved reference. Confirm
that the check being run and the failure being claimed are at the same layer.

---

## 11. Silence is a finding

Read for what the report does *not* say:

| Absent | What it usually means |
|---|---|
| The ⛔ NOT-DOING list is not walked item by item | Something on it was done, or nobody re-read it |
| A metric appears without its prior value | §4 |
| "Stable" with no run count, or a run count with no shared-factor statement | §3 |
| An inference section that is empty | Inferences were written into the verified section |
| No "where this process was wrong" content, or "everything was fine" | That section was skipped |
| A deferred item with no reopen condition | It is forgotten, not deferred |
| A behavior flag exercised only in its default position | §9, and it is usually the non-default branch that touches money |

---

## 12. Verdicts

**You are not the end of the workflow.** Your verdict returns to the
orchestrator, which decides what happens next:

```text
Implementation report ──► VERIFICATION ──► verdict ──► Orchestrator
                                                        accepts / re-sequences /
                                                        dispatches the next work
```

Do not select the next task, open a follow-up stage, or fix what you found.
A defect you discover is a finding with a verdict attached; turning it into
work is the orchestrator's call, and fixing it yourself destroys the
independence that made finding it possible.

Return exactly one verdict, with the evidence that produced it:

- **ACCEPT** — every load-bearing assertion re-run, with pasted output.
  `EXECUTOR_DONE` is not `VERIFIED`; only your own re-run makes it so.
- **REJECT** — name the specific claim, what you ran, and what you got.
  Reject the claim, not the report.
- **BLOCKED** — the acceptance oracle doesn't exist, or a required decision
  is open. This is a legitimate outcome and must not be converted into a
  conditional accept.

For anything you could not verify, say so explicitly. **An unverified item
must never be written as verified** — including by omission. If you re-ran
four of six assertions, the report says four of six.

⚠ Report separately anything that changes the plan rather than the verdict:
an assumption that no longer holds, a dependency pointing the other way, a
regression surface wider than the brief assumed. That is project-model
information, and the orchestrator needs it even when the verdict is ACCEPT.

---

## Boundaries

**Do not verify what you materially authored.** If you wrote the artifact,
say so and have a separate session re-run the assertions; a self-review
inherits the same incomplete premise set that produced the defect.

You may read anything, run anything, and write throwaway probes. You should
not modify the artifact you are certifying — a fix and its acceptance are two
stages, and merging them removes the only independent check.

Keep this skill about challenging a claim. How a change is *produced* —
scope discipline, root-cause location, escalating open decisions — is
`../implementation/SKILL.md`.
