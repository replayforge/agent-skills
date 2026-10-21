---
name: task-night
description: >
  Keep an orchestrator session working while the user is away (overnight,
  after hours): schedule wake-ups in this session so that when an API usage
  limit resets, stopped background sessions are resumed and the loop
  (collect → accept → merge → dispatch) carries on without anyone at the
  keyboard. Takes an optional reset time from the user ("04:00", "+3h");
  otherwise tries to read it from stopped sessions, and always adds a
  periodic heartbeat so an unknown reset time is still covered. Use when the
  user types /task-night, or says "我下班了", "晚上繼續跑", "rate limit 之後自己醒來",
  "幫我排喚醒", "keep going overnight". Cancel with "/task-night off" when the
  user is back.
license: MIT
---

# /task-night

Why this exists: an overnight run in the reference project stopped at 01:00 on
the usage limit and nothing moved until a one-shot wake-up at 04:00 — two
earlier wake-ups had already fired and deleted themselves, and nothing else
was scheduled. A reset time nobody wrote down, or a single one-shot, leaves
hours on the table.

## 0. Before anything

If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules win.

## 1. When to wake

In order, take the first that gives a time:

1. **The user's argument**: `04:00`, `4am`, `+3h`. Use it as given.
2. **Detect**: from the repository root,
   ```bash
   bash <this skill's base directory>/reset.sh
   ```
   It searches the screen output of this repo's stopped background sessions for a "resets …" phrase and prints what it finds, or `none`. ⚠ Best effort: the phrase is read off rendered output, and its wording is not a stable interface — show the user the matched line rather than only the parsed time.
3. **Unknown**: no one-shot; the heartbeat in §3 covers it.

Add 3 minutes to a known reset time (the limit lifts at the reset instant, not before).

## 2. Write down what to do on waking

Wake-ups start from a cold context. Before scheduling, update the session-state file as `/task-session-update` describes (`$(git rev-parse --git-common-dir)/session-state.md`), with a **「醒來要做」/ on-wake** list: which sessions to resume, which verdicts to dispatch, which waiter scripts to restart, which questions are parked for the user.

## 3. Schedule (CronCreate)

- **One-shot** at the reset time from §1, if there is one: `recurring: false`, minute/hour/day/month pinned.
- **Heartbeat**, always: recurring, every 2 hours at an off-minute (e.g. `7 */2 * * *`), so an unknown or wrong reset time costs at most two hours. If the user gave the hours they are away, restrict the hour field to them.

Both use the same prompt, written in the user's language, for example:

```text
[排程喚醒] 使用者不在：不要問使用者，要決定的事記在 session-state「等使用者」。
先讀 $(git rev-parse --git-common-dir)/session-state.md，照「醒來要做」執行：
① claude agents --json --all 找停住的背景 session（完整 sessionId）；已交結果的先 claude rm；
② 其餘用 /task-continue 續跑（先 --dry-run）；
③ 派還沒派的驗收或下一輪，重開背景等待；
④ 照流程繼續（收件→驗收→合併→派下一輪），最後更新 session-state。
若還在用量上限內，什麼都不做，等下一次喚醒。
```

Tell the user the **actual next run times** CronCreate/CronList returned (the scheduler shifts jobs), and these limits:

- ⚠ Jobs live only in **this** session: closing the terminal or the session cancels all of them.
- ⚠ They fire only while the session is idle; a long turn delays them.
- ⚠ Recurring jobs expire after 7 days.

## 4. `/task-night off` — the user is back

`CronList`, then `CronDelete` every job this skill created (match the prompt's first line). Report what ran overnight: read session-state and the git log since the user left.

## Boundaries

- It schedules and resumes. Acceptance, merging and dispatch on each wake follow the project's own rules (`engineering-orchestrator`, the notes file).
- ⛔ Do not resume a session whose stage already has a committed result — `/task-continue` step 3 applies on every wake.
