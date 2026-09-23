---
name: engineering-project-records
description: >
  Write the durable markdown that crosses sessions so another role can find
  the right entry by grep and tell whether it is still true: stable IDs that
  double as search keys, append-only ordering, scannable index tables, closed
  status vocabularies, keeping overturned conclusions without misleading the
  next reader, putting a warning at every point a search can land, and a
  mechanical check on the parts that rot. Use when creating or editing any
  document another session will read, or when the user says
  "這份 md 該怎麼寫", "文件怎麼整理", "怎麼搜尋這些文件", "編號怎麼定",
  "findings 要怎麼記", "readme 要寫什麼", "register", "索引". Do NOT use to
  decide what belongs in which register — that is the workflow constitution.
argument-hint: "[register|index|brief|report|audit]"
license: MIT
---

# Engineering Project Records

## Related skills

- `../work-flow/SKILL.md` — which registers exist and what each is for.
- `../orchestrator/SKILL.md` — governs the registers; this file is how to write them.
- `../research/SKILL.md` / `../implementation/SKILL.md` / `../verification/SKILL.md` — produce most of the content.
- `../knowledge-capture/SKILL.md` — a different destination: reusable lessons leaving the project. Project records are the project's own operational state and stay in the repository.

---

## The two failures this prevents

A cross-session document fails in exactly two ways, and both are silent:

1. **Nobody finds it.** The fact was recorded; the next session searched with
   a different word and re-derived it, or worse, decided the opposite.
2. **Somebody finds it and can't tell whether it's still true.** Registers
   accumulate by round. A grep hit may land in a conclusion that was
   overturned two rounds later, in the same entry.

Everything below is aimed at one of those two.

> The reader is **another role, in another session, with no context, under
> time pressure, arriving by `grep`.** Write for that reader, not for
> someone reading top to bottom. Nobody reads these top to bottom.

---

## 1. The ID is the search key

Give each register one prefix, and make the ID appear **verbatim in both the
documents and the code**:

```text
F- / C- / D- / E-   findings.md    F = source defect, C = contract gap,
                                   D = conversion decision, E = not yet mapped
B-                  bugs.md        defects we introduced; every one has a disposition
T-                  traceability   an implemented behavior ← its legacy basis
R-                  findings       verified observations, including overturns
DEC- / RISK-        registers      decisions and risks
Rule n              rules.md       a constraint and the incident that earned it
```

Because the ID is the key, one command answers "what was decided, where is it
implemented, what does it touch":

```bash
grep -rn "F-17" docs/ src/
```

**Fix the citation format and never vary it.** Two forms, because they are
read from different places:

| Where | Form | Why |
|---|---|---|
| Inside another document | `findings.md F-17` | short; the reader is already in `docs/` |
| In a code comment | `docs/findings.md F-17` | repo-relative; the reader is not |

⚠ A markdown **link target** is a third thing and resolves relative to the
file containing it. A move once left every text reference correct and six
links broken, with `grep` for the old path returning zero. **Grep-clean does
not mean links resolve — run a link checker.**

---

## 2. Append; never insert

New entries go at the **end of their section**. Inserting in the middle
renumbers nothing but invalidates every cross-reference that points past the
insertion point, and those references live in other files and in code.

This has a direct consequence: **any index carrying line numbers goes stale
on every append.** Do not solve that by dropping the line numbers — solve it
with a check (§6).

---

## 3. Any register long enough to scroll needs an index table

Put it at the top, and say what it is for:

```markdown
## Index (112 entries — scan this, don't read the file)

| ID | One line | Status | Line |
|---|---|---|---|
| **F-17** | Jackpot trigger reads the wrong enum | ✅ ruled: fix | 363 |
| **F-29** | 🔴 Seven close buttons were live all along | ⛔ overturned | 2293 |
```

Four columns, and each earns its place:

- **ID** — the search key.
- **One line** — deliberately *not* machine-checked against the heading. A
  human-written summary is the whole value of the index; a generated one just
  repeats the title.
- **Status** — used as a filter while scanning. Keep it a **closed
  vocabulary** (§4).
- **Line** — so the reader jumps straight in: `sed -n '363,+40p' findings.md`.

Mark long entries so a hurried reader can skip: *"entries marked 📖 are ≥ 60
lines of verification narrative — **the conclusion is in the heading**."*

---

## 4. Status is a closed vocabulary, and every entry has one

An entry with no disposition turns the register into a wish list. Publish the
vocabulary next to the index so it can be used as a scan filter:

```text
🔒 preserve       a defect in the old system that we deliberately do not fix
✅ fixed          with the commit
✅ ruled: fix     a behavior change that a human approved
⛔ overturned     an earlier round's conclusion was wrong
📝 PROPOSED       contract not yet settled
⏳ pending        undecided
⏸ deferred       with a decidable reopen condition — never "later"
```

**"Deferred" without a reopen condition is "forgotten".** Make the condition
something a reader can evaluate: not *"when we do the squeeze variant"* but
*"when the backend can report per-slot editability **and** the
`AdminSetSingleResult` command exists"*.

---

## 5. Overturns stay — so warn the searcher

Never delete a conclusion that turned out to be wrong. Keep the old
conclusion, the new evidence, and **where the old reasoning broke** — deleting
it guarantees the same mistake recurs and leaves dangling references.

But that creates the search hazard: **the old and new conclusions live in the
same entry, and grep lands on either.** So:

1. **Mark the heading** — `### 🔴 F-29 …` — and make the marker greppable:
   `grep -n "⛔ overturned" findings.md` must list every one.
2. **Put the operative conclusion at the end of the entry**, under a fixed
   label (`→ ruling:`), always in the same place.
3. **Say this explicitly in the index document**, as a procedure:

> ⚠ After a grep hit, scroll **up to the nearest `###` heading** and check for
> an overturn marker before believing what you found. Example: searching for
> `"only handles minor and grand"` hits the full text of an old conclusion
> that was overturned three rounds later.

That paragraph is the single highest-value thing in a docs README.

---

## 6. Put the warning where the search lands

A caveat at the top of a section protects only readers who arrive at the top.
Readers arrive by grep, in the middle.

> Nine rows in a URL list produced known-wrong screenshot baselines. The
> explanation was written once in the section header — and then **one warning
> line was added directly above each of the nine rows, each naming that row**,
> so `grep dlg_logout` shows it without scrolling up.
>
> The stated reason: otherwise the next person sees nine differences and goes
> hunting for a bug that does not exist.

→ Duplicate a warning as many times as there are places someone can land on
the thing it protects. This is the one context where repetition is correct.

---

## 7. Every claim carries its source; every rule carries its provenance

- A behavior's basis is **a real filename and line**, plus which branch or
  path that line is on. Never "refer to the legacy system", never "see the
  existing implementation".
- A rule states **the incident that earned it**. A rule without provenance is
  treated as dogma and bypassed the first time someone judges "this case is
  different" — and the case usually *is* different, for a reason that does
  not apply. Knowing what an incident cost is what makes that judgment
  possible.
- Mark which entries came from **this project's own incidents** versus
  inherited best practice. They have different authority when they conflict.

---

## 8. Guard the parts that rot

Counts in prose — "38 rows", "C-01 through C-46", "ten documents" — change
every round and nobody updates them.

Put the machine-derivable ones under a check that computes the real value
from the content and exits non-zero on drift, then **list which numbers are
governed** so adding a new one means adding a row:

```text
check:doc-counts     counts stated in prose vs counts derived from content
check:index          every body entry is in the index; every index line
                     number really is that entry's heading; no stale rows
fix:index            recompute the line numbers
link-check           every relative markdown link resolves
```

Two rules about these checks:

**State what each check proves and what it does not.** One coverage checker
carries in its header: *"this proves every id has a disposition — not that it
was drawn correctly."* Without that line, a green check acquires a meaning
nobody granted it.

**Check only the mechanically decidable part.** The index checker
deliberately does *not* compare the one-line summary against the heading,
because a human-written summary is the point. A check that fights the
document's purpose gets disabled.

⚠ Add a check after a problem occurs **twice**, not preemptively. Before
twice you are guessing at the failure mode, and a check that misfires teaches
people to ignore it.

---

## 9. The index document is a router, not a summary

The top-level README's job is to get a reader to the right file in under a
minute — not to restate the contents.

Include, in this order:

1. **One row per document: the question it answers, and when to read it.**
   Phrase it as the question, not the topic — *"why is this behavior like
   this?"* beats *"traceability matrix"*.
2. **A first-time reading order**, with what to skip. Say which file is a
   lookup table rather than a read.
3. **Which file goes stale fastest**, and how to tell — *"check `git log -1`
   on it first."*
4. **How to search** — the ID scheme, and five copy-pasteable commands that
   answer the questions people actually have. The most valuable is usually
   the reverse lookup: *given this line of the old system, what did we decide
   about it?*
5. **The grep hazard** (§5).
6. **"I want to know X → go here."** A plain table. This is what a new
   session actually uses.

---

## 10. What each role needs to be able to find

The registers are a handoff protocol. Each role arrives asking a different
question, and each question needs a guaranteed entry point:

| Arriving role | Asks | Must be answerable by |
|---|---|---|
| **Orchestrator** | What is settled, what is open, what is next and why? | The project model's known/unknown lists; roadmap ordering with reasons; the dependency graph; open decisions; every deferred item's reopen condition; which stages are `INVALIDATED` or `SUPERSEDED` and why |
| **Research** | What is already known, and what was already ruled out? | ID search across registers; overturn markers; explicitly recorded out-of-scope decisions |
| **Implementation** | Why is this like this, and what am I forbidden to touch? | Behavior → source line; rules with provenance; `preserve` entries |
| **Verification** | What does this claim rest on, and what was never measured? | Per-claim evidence; the inference section; what each check does not prove |

→ **Anything that must be findable by a role other than its author needs an
ID.** A decision recorded only in a result report is findable only by someone
who knows which round it happened in.

⚠ **An invalidated stage is a record, not a deletion.** When new evidence
kills a planned stage, keep the entry, mark it, and say which evidence killed
it — otherwise the next review re-derives the same plan from the same stale
assumption.

→ Conversely: **recording that something was deliberately not done is as
important as recording what was done.** An omission with no entry is read by
the next session as already finished.

---

## 11. Repeated documents use a fixed skeleton

Briefs and reports repeat, so make the sections identical every time — a
missing one becomes visible by shape rather than by careful reading.

Getting this wrong is cheap to detect and cheap to fix: when two consecutive
sessions each had to invent the same missing section, that was the signal the
template was wrong, not that those sessions were unusual.

And keep the naming mechanical: if stage briefs are `stage-NN-topic.md`, the
result is `stage-NN-topic-result.md` in the same directory. A template that
disagrees with its own examples has been found by more than one project.

---

## 12. Protect the evidence from the format

Check what your renderer does to your content before trusting it. One series
puts algorithms and field lists in code blocks rather than tables
specifically because the publishing platform's table renderer alters symbols
inside cells — and an algorithm that loses one character is worse than no
algorithm.

The same applies to editors that reflow, normalize unicode, or strip
trailing whitespace inside fenced blocks.

---

## When not to

Do not create a document to satisfy a list in some skill, including this one.
Reuse the project's existing information architecture when it already serves
the purpose.

Scale the apparatus to the project. A short-lived effort needs IDs and
reopen conditions far less than a multi-round migration where a stale
conclusion propagates silently.

⚠ Periodically ask **when each document was last actually read**. If the
records grow faster than the work they protect, the scaffold has become the
building — and the right response is to delete, not to add another index.

---

## Boundaries

This skill is about the *form* of the project's written state — findability,
citation, status, ordering, mechanical guards. **What** goes in each register
is `../work-flow/SKILL.md`; **who** governs them is
`../orchestrator/SKILL.md`; extracting a reusable lesson out of the project
entirely is `../knowledge-capture/SKILL.md`.
