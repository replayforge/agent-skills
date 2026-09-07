# agent-skills

Reusable agent skills for engineering workflows.

## Skills

### engineering-knowledge-capture

Captures durable engineering lessons from coding, debugging, architecture, benchmarks, incidents, and reviews. It discovers an available note-capable MCP, inspects the notebook hierarchy before writing, composes the note as Markdown, and routes it into the existing knowledge structure instead of dumping session logs.

The skill is designed to work especially well with Notion MCP, but it does not hard-code a private workspace ID or page URL. It discovers the current Knowledge root, reads nearby workspace rules, reuses an existing topic when possible, and only creates a topic when the notebook structure actually needs one.

### Zed

Zed loads skills from `~/.agents/skills/` globally or `<worktree>/.agents/skills/` per project. Copy or symlink the `engineering-knowledge-capture` folder into one of those locations.

Zed can also import a skill from a GitHub Markdown URL with the command palette action `agent: create skill from url`. Import `engineering-knowledge-capture/SKILL.md`.

## Design rules

- Knowledge is not a development diary.
- Raw logs, benchmarks, incidents, and project history stay as source material; only reusable conclusions become Knowledge.
- Existing notebook information architecture wins over assumptions in the skill.
- Do not create a new category for every note.
- Never persist secrets, credentials, private keys, seed phrases, or tokens into ordinary knowledge notes.
