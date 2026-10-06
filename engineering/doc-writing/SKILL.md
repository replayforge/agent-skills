---
name: engineering-doc-writing
description: >
  Write-time discipline for any document another session will act on — task
  briefs, handoff prompts, register rows, reports: every sentence about the
  present state is measured now or written as a question (in scope, traps and
  acceptance clauses too, not only the pre-flight table); never restate another
  document from memory; a row that is read every turn holds the current state
  only and pushes its history into an append-only file; emphasis markers are a
  budget; a read-back pass catches self-contradiction and lost negations; a
  script checks the shapes. Use whenever you are about to write or commit such
  a document, or when the user says "文件品質下降", "任務書寫錯", "寫文件的規則",
  "文件越寫越長", "標記太多", "doc quality", "brief got it wrong". Do NOT use for
  how registers are structured or searched — that is engineering-project-records.
license: MIT
---

# Engineering Doc Writing

## Related skills

- `../project-records/SKILL.md` — the **form** of a durable document (IDs, index, overturns, warnings where grep lands). This file is the **act of writing** one.
- `../orchestrator/SKILL.md` §4 — pre-flight for a brief's fact table, and `check_forbid_negation.py`. This file extends the same rule to every sentence of every document.
- `../doc-fit/SKILL.md` — making a finished document readable for an outside reader.

---

## What this prevents

Documents produced in volume degrade quietly. In the reference project, on one
day, **four of four** implementation reports opened with a "§mismatch" against
their brief — and every mismatch was the orchestrator's, not the executor's:

| Brief said | Measured | Where the sentence sat |
|---|---|---|
| "the existing SIGINT test still passes" — and made it an acceptance clause | no such test existed | **scope and acceptance**, not the pre-flight table |
| "on macOS use `ps -o ignored,caught`" | those keywords do not exist on macOS | the traps section |
| "grep returns 3 lines" | 4 | pre-flight table |
| "add a sentence above the table" and "no diff before the table" | mutually exclusive | scope vs acceptance, same brief |

The measured cause was not carelessness. It was the input: the register the
orchestrator reads before every brief had grown to 270 KB — 140 status rows
averaging 1–2 thousand characters, two emphasis markers per line — while a
cost rule said "do not read large files whole". So briefs were written from
fragments and from memory of fragments.

The fix is on the writing side. A reading rule that saves cost is right **only
if the document read every turn is small**; fix the document, not the rule.

---

## 1. A sentence about the present is a measurement

"Existing X", "currently Y", "Z is at line N", "use command W to see it" —
each is a claim about the repository **now**. Before writing it:

- run the command, and put the evidence **on the same line**: `file:line`, a
  commit SHA, the command in backticks, or a strength tag (`【single-key】`,
  `【someone else's, not re-run】`);
- or, if you will not measure it, **write it as a question for the executor**:
  "check whether a SIGINT test exists; if not, add one".

This applies to **every section**. The pre-flight table is where you are
careful; scope rows, trap notes and acceptance clauses are where the
unmeasured sentence hides — and an acceptance clause resting on a thing that
does not exist is a clause that cannot go red.

## 2. Never restate another document from memory

The sentence "141 covered SIGINT" was a memory of a row that *mentioned*
SIGINT. Summaries drift by one word per hop, and one word ("mentions" →
"tests") is enough.

- Quote the source, or re-open it and cite `file:line`.
- A register row is a summary. The report or verdict file is the source —
  cite that.
- A conclusion overturned by a later verdict is not citable. Check the
  verdict before quoting the report it judged.

## 3. Copying a template copies its errors

A brief built from the previous brief inherits its wrong facts and its lost
negations ("⛔ `--force`" with the "do not" gone). After copying: re-measure
every factual line (§1) and run the checks (§6) **before** editing anything
else, so the inherited errors surface separately from your own.

## 4. A row read every turn holds the current state only

`project-records` §5 says overturned conclusions stay. They stay — **in a
history file**, not in the row everybody reads.

- **Status row**: current verdict, one sentence of reason, who picks it up
  next, and any **still-active** lock, hold or prohibition. Nothing else.
- **History**: an append-only file beside it, rows copied verbatim, with one
  pointer from the status table. Lossless, so it can be checked by set
  comparison.
- When something is released (a hold lifted, a prohibition satisfied), **edit
  the row** — do not append "✅ released" after "🔒 locked". Appending is how a
  row reaches two thousand characters.
- Budget the row (`check_doc_write.py` flags table rows over 600 characters).
  A row that will not fit is telling you the history has not been moved out.

## 5. Emphasis markers are a budget

A marker on every line marks nothing. When the reference register reached
two markers per line, readers could not tell a live prohibition from a
historical one, and writers matched the density.

- One marker per prohibition, on the prohibition. Not on its explanation.
- A marker for history is wrong: history is not a warning.
- Remove a marker when the thing it marks is no longer true.

## 6. Read it back before committing

Three passes, in this order:

1. **Contradiction**: for each scope row, find the acceptance clause that
   checks it, and ask whether both can be satisfied at once. Two clauses that
   cannot be satisfied together stop the executor to guess which one wins.
2. **Negation**: `python3 ../orchestrator/check_forbid_negation.py <files>` —
   a "⛔" that lost its "do not" is an order.
3. **Shapes**: `python3 check_doc_write.py <files>` (this directory) —
   `CLAIM` lines with a state word and no evidence on the line, `ROW`s over
   budget, `MARK` overload (≥ 4 on one line, or > 1.0 per line in the file).
   Mark a line that is not a state claim (a column called "current status")
   with `<!-- doc-ok -->`. Run only on the text you added when the file has
   old, unfixable hits.

⚠ What the script proves: that every state sentence **has** a re-runnable
source beside it. It does not prove the source says what the sentence says.
A green `CLAIM` is the floor, not the check.

## 7. One parseable field per item

If a tool reads the document, give each item its own field. A verification
file carrying two verdicts ("140 ACCEPT, 143 REJECT") was read by the status
board as a single ACCEPT — the first bold keyword wins. Two verdicts → two
rows or two files, never one line.

---

## When not to

Throwaway notes and a document only you will read in the next hour. The rules
pay off when another session will **act** on the document without asking.

## Boundaries

This skill governs how a document is written. Which register an item belongs
in is `work-flow`; how a register is laid out and searched is
`project-records`; whether a brief's facts are the right ones to gather is
`orchestrator`.
