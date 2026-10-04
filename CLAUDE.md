# Knowledge Vault: project context

Shared context for the main agent and every subagent. Read this instead of exploring the codebase; open only the files your brief names.

## What this is
A personal knowledge vault: notes, research findings and Claude's memory across projects as plain Markdown files (Obsidian-compatible), with search, a graph view, and a way for Claude Code sessions to read and write it (for example an MCP server). Owner: the user (single user, Windows 11).

**Current stage:** Phase 0 setup, then Discovery 1 (ideation). Nothing below "TODO" is decided; do not build on guesses.

## Stack and commands
TODO (decided in the tech-stack discovery phase).
- Run: TODO
- Test: TODO

## Directory layout
- `docs/`: vision, decisions, data model, specs. The source of truth for what to build.
  - `docs/vision.md`: problem, users, must-haves, non-goals, success criteria (Discovery 1)
  - `docs/decisions.md`: decision log (chosen, rejected, why)
- `README.md`: short public description

## Modules index
TODO (filled once there is code: module, key functions and signatures).

## Conventions
- English is American spelling. No em dashes in prose, UI text, comments or docs.
- Every feature has acceptance criteria a test or browser check can confirm.
- Tests fake external services: TODO (how, once the stack is chosen).
- Browser checks and experiments use a throwaway copy of vault data, never the user's real vault.

## Content rules
TODO (from the vision: what goes in the vault, privacy rules, what Claude may write).

## Plans and decisions
- Progress and phase plans: Orchestra board (https://claude.ai/artifact/Eqis6DgyZMefwhzFM1KNta), project id `knowledge-vault`, phase prefix `kv~`.
- Decisions: `docs/decisions.md`. A forced change updates the spec and the decision log in the same commit.
