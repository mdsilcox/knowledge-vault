# 5. The vault skill

A Claude Code skill (`~/.claude/skills/vault/SKILL.md`) that tells any session when to use the vault and how to write to it. The global CLAUDE.md section points to it in two or three lines, so sessions that never need the vault pay almost nothing.

## Content of the skill
- **When to search** (only these): starting research or a stack choice; hitting an error or problem that might have been seen before; the owner asks ("check the vault", "have we solved this before?"). One search, then read the top one or two notes; don't browse.
- **When to write** (the agreed moments): after a research report; when a decision is logged; at a phase retro; when a problem is solved in a way worth reusing; whenever the owner says so.
- **How to write:** search first and update a close match instead of duplicating; pick the type and folder from the data model; title as a short claim; fill the template's sections briefly; set `project`, `tags`, `created`, `status: active`, `source`; link related notes. The hook adds the project link, updates the hub and pushes, so Claude doesn't.
- **Ask first** before deleting, moving or superseding a note; before writing anything that might be sensitive or personal; before rewriting most of an existing note.
- **Tools to use:** `search_notes`, `read_note`, `write_note`, `edit_note`. Ignore the project, workspace, schema and cloud tools.
- **Never:** secrets; whole transcripts or copies of project docs (link with `source`); one-project trivia that belongs in that project's memory.

## Acceptance criteria (scenario checks in a live session at the Build gate)
- **Given** a session in another project, **when** asked "have we dealt with Windows install paths breaking imports before?", **then** Claude searches the vault once and answers from the pattern note.
- **Given** a research report hand-back, **then** Claude writes a `research` note and a `finding` per key fact without being asked, and they reach GitHub.
- **Given** an existing note on the topic, **when** a related fix is found, **then** Claude edits that note instead of creating a new one.
- **Given** a session that never touches the topic, **then** no vault tool is called.
- **Given** a request to delete a note, **then** Claude asks before deleting.
