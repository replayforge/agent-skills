---
name: engineering-doc-fit
description: >
  Make a document read smoothly for a named outside reader (a PM, a new hire, a
  partner team) who has none of the project's context: a fresh session reads it
  cold as that reader, lists every point where the text jumps (undefined term
  or ID, missing why, assumed history, section that starts mid-thought), then
  fills each gap from the repository's own sources — adding context without
  changing any fact, number, decision or quoted word, which a script checks.
  Use when the user says "以 PM 角度補脈絡", "讀起來很跳", "別人看不懂", "補齊文檔脈絡",
  "fit this doc for", "make this readable for". Do NOT use to change what a
  document decides.
license: MIT
---

# Engineering Doc Fit

The author cannot see where their own document jumps: every gap is filled in
by memory while re-reading. So the read is done by a session that has **no**
memory of the project — and the rewrite is checked by a script, because a
session asked to "add context" also tends to smooth away the inconvenient
precise bits.

## Inputs

- `path` — the document.
- `reader` — who it is for, in one line (e.g. "PM，懂產品與現場，不讀程式碼、不知道本倉庫的編號制度").
  Ask if missing; the reader decides what counts as a jump.
- optional free-text instructions from the user (`--<提示詞>`).

## Steps

1. **Snapshot**: copy the original to a temp file (`$TMPDIR/doc-fit-orig.md`).
2. **Dispatch one fresh session** (a background subagent or `claude --bg`; ⛔ not
   this session — it has the context the reader lacks). Hand it only: the
   path, the reader line, the user's extra instructions, the repository root,
   and the brief below. Nothing from this conversation.
3. When it returns: run
   `python3 <this skill's base directory>/check_doc_fit.py "$TMPDIR/doc-fit-orig.md" <path>`.
   Exit 1 ⇒ a fact, number, ID or quote was dropped or changed: restore it
   (or reject the rewrite) before anything else. Then `git diff` and read
   every added sentence for **new claims** — an added "because …" that the
   sources do not support is worse than the gap it filled.
4. Report to the user: the jump list (before/after, one line each) and the
   items marked ⏳ (gaps the sources could not fill — those are questions for
   the user, not for the rewriter). Commit only per the project's rules.

## Brief for the fresh session

```text
You are <reader>. You have never seen this project. Read <path> top to bottom
once, as that reader, before opening anything else.

Phase 1 — jump list. Every place you had to stop, one row each:
  where (section + first words) | kind | what you needed to know
Kinds: undefined term or abbreviation; bare ID / code name (DEC-…, stage-…,
function names) with no plain meaning; missing "why" behind a rule or a
recommendation; assumed history ("as decided", "上次說的"); section or table
that starts without saying what it is for or how it relates to the previous
one; option labels (甲/乙, A/B) whose difference is not stated; register
switch (plain prose → internal jargon).

Phase 2 — fill. For each row, add the missing context IN PLACE, using only
sources inside the repository (grep the decision register, glossary, linked
docs). Keep the reader's language and tone.
Hard rules:
  - ⛔ Do not delete, reword or reorder any fact, number, date, ID, option,
    recommendation, or text inside 「」 / “” / `code`. Add around them.
  - ⛔ Do not add a claim you cannot point to a source for. If the sources do
    not say, write the gap as "⏳ 待確認：<question>" instead of guessing.
  - Prefer one short bridging sentence or a glossary row over a paragraph.
    If the document grows by more than ~30%, stop and report instead.
  - Write only to <path>. ⛔ Do not commit.

Report: the jump list with, per row, "filled (source: …)" or "⏳".
```

## Why the check exists

"Add context" invites paraphrase, and paraphrase is where a 15-second timeout
becomes "a short timeout" and a user's exact words become a summary. The
script compares every ID, number, code span and quoted phrase between the two
versions (as a multiset); a rewrite that only adds cannot fail it.
`--self-test` has the positive and negative cases.
