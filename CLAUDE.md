# Knowledge Vault: project context

Shared context for the main agent and every subagent. Read this instead of exploring the codebase; open only the files your brief names.

## What this is
A personal knowledge vault: notes, research findings and Claude's memory across projects as plain Markdown files (Obsidian-compatible), with search, a graph view, and a way for Claude Code sessions to read and write it (for example an MCP server). Owner: the user (single user, Windows 11).

**Current stage:** Discovery 1 done (vision, stack, spike); next is D2 (data model, spec, roadmap). Anything marked TODO is undecided; do not build on guesses.

## Stack and commands
- **Vault server:** [basic-memory](https://github.com/basicmachines-co/basic-memory) 0.23+ as a user-level MCP server, hybrid search (SQLite full text plus FastEmbed `bge-small-en-v1.5` in sqlite-vec). Index lives outside the vault (`~/.basic-memory/memory.db`, or `BASIC_MEMORY_CONFIG_DIR`). Decisions and reasons: `docs/decisions.md`; measurements and gotchas: `docs/spike.md`.
- **Runtime:** Python 3.12+ via uv (system Python is 3.11; never install basic-memory with the system pip).
- **Vault:** plain Markdown in the private repo `mdsilcox/knowledge-vault-data`; PC writes and pushes, iPhone reads with Obsidian plus the Obsidian Git plugin (cloned into a `vault` subfolder).
- **This repo** holds conventions (templates, layout, a skill, sync scripts, user guide), not a server.
- Run: TODO (install and MCP registration commands, Build 1)
- Test: TODO (Build 1)
- Windows gotchas: set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` for the `bm` CLI; keep installs in short paths.

## Directory layout
- `docs/`: vision, decisions, data model, specs. The source of truth for what to build.
  - `docs/vision.md`: problem, users, must-haves, non-goals, success criteria (Discovery 1)
  - `docs/decisions.md`: decision log (chosen, rejected, why)
  - `docs/research/`: research reports (`d1-survey.md`)
  - `docs/spike.md`: D1 spike results, measured costs, phone setup procedure
- `README.md`: short public description

## Modules index
TODO (filled once there is code: module, key functions and signatures).

## Conventions
- English is American spelling. No em dashes in prose, UI text, comments or docs.
- Every feature has acceptance criteria a test or browser check can confirm.
- Tests fake external services: TODO (how, once the stack is chosen).
- Browser checks and experiments use a throwaway copy of vault data, never the user's real vault.

## Content rules
- Two repos: this one (`mdsilcox/knowledge-vault`, public) holds tool code and conventions only. Vault notes live in `mdsilcox/knowledge-vault-data` (private). Never commit vault content here.
- The vault holds only key, reusable findings, linked back to their source project; per-project memory stays where it is.
- Full rules: `docs/vision.md` (what goes in, writing moments, non-goals).

## Plans and decisions
- Progress and phase plans: Orchestra board (https://claude.ai/artifact/Eqis6DgyZMefwhzFM1KNta), project id `knowledge-vault`, phase prefix `kv~`.
- Decisions: `docs/decisions.md`. A forced change updates the spec and the decision log in the same commit.
