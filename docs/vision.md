# Vision: Knowledge Vault

**Status:** draft for approval (Discovery 1, 2026-10-04)

## Problem
Research and discovery happen inside each project, and the same kinds of problems keep coming back in later projects. Today the findings stay buried in one project's docs, memory folder or chat transcripts, so each new project starts over. There is no single place where past findings and the solutions that worked can be found by meaning, by the user or by Claude.

## User
One person (the owner), working with Claude Code on Windows 11 across many projects, browsing on a PC and an iPhone. Claude Code sessions and their subagents are the second kind of user: they search the vault and write to it on the owner's behalf. Most notes are written by Claude when the owner asks; the owner mostly reads, browses and asks.

## What goes in (priority order)
1. Claude's key memory across projects: lessons learned, preferences that apply everywhere, reusable patterns.
2. Research findings: what was surveyed, what was found, with sources.
3. The owner's notes.
4. Decisions worth reusing (chosen, rejected, why).
5. Later: reading and bookmarks, journal.

Only key findings go in. Each project keeps its own memory folder and docs; the vault holds the distilled, reusable part, with a link back to the source project. Nothing sensitive is stored today, so there is no privacy tiering in v1.

## Must-haves (v1)
- **Plain Markdown the owner owns.** Notes are ordinary `.md` files with simple frontmatter and `[[wikilinks]]`, opening cleanly in free Obsidian. No database is the source of truth; any index can be rebuilt from the files.
- **Claude can search and write on demand.** Any Claude Code session, in any project, can search the vault by keyword and by meaning, read notes, and create or update notes, through a tool it loads only when needed (an MCP server or equivalent). Claude writes freely and asks the owner only when it judges a note sensitive, contentious or a big change.
- **Semantic search, free and local.** Search by meaning runs on the PC with no paid API.
- **Clear writing moments.** Claude writes to the vault after a research report, when a decision is logged, at a phase retro, when a problem is solved in a reusable way, and whenever the owner says to.
- **Browse anywhere.** The vault lives in a private GitHub repo (`mdsilcox/knowledge-vault-data`) and opens in free Obsidian on the PC and the iPhone, with keyword search, links and the graph view.
- **Seeded with this project's findings.** v1 holds this project's research, decisions and lessons as the first real content.

## Later (not v1)
- Seeding from other projects (Blue Dragon Tuner, Russian Trainer, Orchestration Lab).
- Reading and bookmarks, journal.
- Semantic search on the phone.
- Automatic suggestions of related past findings at the start of a project or phase.
- Privacy tiers for sensitive notes.

## Non-goals
- Anything paid: no Obsidian Sync or Publish, no paid embedding APIs, no paid hosting.
- A custom note-taking app or web UI: Obsidian is the UI.
- Replacing per-project memory or project docs.
- Loading the vault into every session automatically: it is queried only when needed.

## Constraints
- Free only. Windows 11 PC; iPhone for reading.
- Two repos: `mdsilcox/knowledge-vault` (public) for the tool code and conventions; `mdsilcox/knowledge-vault-data` (private) for the notes. Vault content never goes in the public repo.
- Small fixed cost per session (a pointer in the global CLAUDE.md and the tool definitions); the actual figure is measured in the spike.

## Success criteria
1. In a Claude Code session in a different project, asking about a problem this project solved finds the right note by meaning, even when the question uses different words than the note.
2. Claude can file a finding in one step, and the new note appears on the iPhone after a sync, readable and linked.
3. The vault opens in free Obsidian on both devices with a working graph view, and every note is readable in a plain text editor.
4. Deleting the search index and rebuilding it from the files loses nothing.
5. A session that never touches the vault pays only the small fixed cost measured in the spike.
6. Total cost: zero.
