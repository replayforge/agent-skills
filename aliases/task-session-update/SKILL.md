---
name: task-session-update
description: >
  Prepare the orchestrator session for compaction: write the live state
  (running stages, background waits, questions waiting on the user, active
  freezes and exceptions) to <repo>/.git/session-state.md, then hand the user a
  ready /compact line that keeps it. Use when the user types
  /task-session-update, or says "壓縮 session", "壓縮對話", "compact the session".
license: MIT
---

# /task-session-update

⚠ **A skill cannot run `/compact`.** It is a built-in CLI command; only the user can type it. This skill does everything else, so the user's part is one paste.

1. If the repo has `.stage-status.json` with a `notes` path, read that file first — project rules win.
2. Commit what this session owes (own files only, pathspec). Then run the board from the repository root:
   ```bash
   python3 <this skill's base directory>/../../engineering/stage-status/stage_status.py
   ```
3. Overwrite `$(git rev-parse --git-common-dir)/session-state.md` (inside `.git/`: never committed, shared by all worktrees). Keep it under ~60 lines, in the user's language, current state only:
   - **Running / waiting stages**: number, session id, what it is doing, what acceptance it needs.
   - **Background commands**: task id, script path, what wakes it, what to do when it wakes.
   - **Waiting on the user**: each open question verbatim, with the options offered.
   - **Active freezes, holds, exceptions** and the user's words that set them.
   - **Next step** when the session resumes.
   ⛔ No secrets (URLs, table codes, tokens) — point to where they live instead.
4. Reply with the file path and **one copyable line** for the user:
   ```
   /compact 先讀 <path>；保留：<3–6 short items from step 3>
   ```
   Tell them that after compaction the next turn should begin by reading that file.

**Optional auto-restore.** A `SessionStart` hook with matcher `compact` prints the file back into context after every compaction (manual or automatic), so step 4's "read it first" needs no reminder. In `~/.claude/settings.json`:
```json
{ "matcher": "compact", "hooks": [{ "type": "command", "timeout": 5,
  "command": "f=\"$(git rev-parse --git-common-dir 2>/dev/null)/session-state.md\"; if [ -f \"$f\" ]; then echo \"session state (${f}):\"; cat \"$f\"; fi; exit 0" }] }
```
Write `${f}`, not `$f`, before non-ASCII text: bash reads the following multibyte character as part of the name.
