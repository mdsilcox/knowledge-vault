---
title: README
type: readme
---

# Knowledge vault

This repository holds one vault of Markdown notes: the reusable findings, patterns, decisions and research gathered across all projects. It is meant for the owner and for AI agents that search it before starting new work.

## Folders

- `patterns/`: a problem that may recur and the fix that worked.
- `findings/`: facts learned: tool behavior, limits, measurements.
- `decisions/`: choices another project could reuse (chosen, rejected, why).
- `research/`: survey and comparison summaries with sources.
- `notes/`: anything else worth keeping.
- `projects/`: one hub note per project, linking to its notes.

## How it works

- Notes are written by Claude through the basic-memory MCP server. The owner can edit notes in Obsidian on the PC, but the hook only runs on Claude's writes, so hand edits are committed with the next note Claude writes (the hook does `git add -A`), or by committing and pushing manually.
- A hook commits and pushes changes after each note write, so this repository stays current.
- The phone is read-only: browse the notes there, but make changes through Claude.

## Conventions

The full note format and conventions live in the public repository, in `docs/data-model.md`: https://github.com/mdsilcox/knowledge-vault
