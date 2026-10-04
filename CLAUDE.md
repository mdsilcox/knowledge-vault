# Knowledge Vault: project context

Shared context for the main agent and every subagent. Read this instead of exploring the codebase; open only the files your brief names.

## What this is
A personal knowledge vault: notes, research findings and Claude's memory across projects as plain Markdown files (Obsidian-compatible), with search, a graph view, and a way for Claude Code sessions to read and write it (for example an MCP server). Owner: the user (single user, Windows 11).

**Current stage:** D2 (data model, spec, roadmap) in review; acceptance tests are written and red until Build 1. Anything marked TODO is undecided; do not build on guesses.

## Stack and commands
- **Vault server:** [basic-memory](https://github.com/basicmachines-co/basic-memory) 0.23+ as a user-level MCP server, hybrid search (SQLite full text plus FastEmbed `bge-small-en-v1.5` in sqlite-vec). Index lives outside the vault (`~/.basic-memory/memory.db`, or `BASIC_MEMORY_CONFIG_DIR`). Decisions and reasons: `docs/decisions.md`; measurements and gotchas: `docs/spike.md`.
- **Runtime:** Python 3.12+ via uv (system Python is 3.11; never install basic-memory with the system pip).
- **Vault:** plain Markdown in the private repo `mdsilcox/knowledge-vault-data`; PC writes and pushes, iPhone reads with Obsidian plus the Obsidian Git plugin (cloned into a `vault` subfolder).
- **This repo** holds conventions (templates, layout, a skill, sync scripts, user guide), not a server.
- Setup: `uv sync` (Python 3.12+ venv in `.venv`, deps PyYAML and pytest)
- Test: `uv run pytest` (fast, default); `uv run pytest -m slow` (real basic-memory, skips if not installed); `KV_GATE_VAULT=<vault> uv run pytest -m gate` (Build gate checks on the real vault)
- CLI: `uv run python -m kv check <vault>` | `sync --vault <vault>` (the hook) | `install [--dry-run]`
- Windows gotchas: set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` for the `bm` CLI; keep installs in short paths.

## Directory layout
- `docs/`: vision, decisions, data model, specs. The source of truth for what to build.
  - `docs/vision.md`: problem, users, must-haves, non-goals, success criteria (Discovery 1)
  - `docs/decisions.md`: decision log (chosen, rejected, why)
  - `docs/research/`: research reports (`d1-survey.md`)
  - `docs/spike.md`: D1 spike results, measured costs, phone setup procedure
  - `docs/data-model.md`: note types, frontmatter, layout, links, lifecycle, invariants (the first contract)
  - `docs/spec/`: one spec per feature with Given/When/Then criteria; `README.md` there holds the code contract
- `kv/`: the Python package (glue around basic-memory, not a server)
- `tests/`: acceptance tests; `conftest.py` has the vault and git fixtures; `fixtures/spike_notes.py` is the spike's 15-note vault
- `templates/`, `skill/`, `vault-seed/`: note templates, the vault skill, files seeded into the data repo
- `README.md`: short public description

## Modules index
Signatures are the contract in `docs/spec/README.md`; stubs raise NotImplementedError until Build 1.
- `kv/notes.py`: `parse_note(path) -> Note`, `wikilinks(text) -> list[str]`
- `kv/secrets.py`: `find_secrets(text) -> list[str]`
- `kv/check.py`: `check_vault(vault) -> list[Problem]`, `main(argv)`
- `kv/hubs.py`: `ensure_project_links(vault)`, `update_hubs(vault)`; markers `START`/`END`
- `kv/sync.py`: `handle_hook(payload, vault) -> SyncResult`, `main(argv)`; `MATCHER` for the hook
- `kv/install.py`: `merge_settings(settings, hook_command)`, `merge_claude_md(text)`, `main(argv)`
- `kv/__main__.py`: CLI dispatch

## Conventions
- English is American spelling. No em dashes in prose, UI text, comments or docs.
- Every feature has acceptance criteria a test or browser check can confirm.
- Tests fake external services: GitHub is a bare git repo in `tmp_path`; basic-memory runs only in `slow` tests with `BASIC_MEMORY_CONFIG_DIR` in `tmp_path`. Never the real vault, `~/.basic-memory` or `~/.claude` in tests.
- Browser checks and experiments use a throwaway copy of vault data, never the user's real vault.

## Content rules
- Two repos: this one (`mdsilcox/knowledge-vault`, public) holds tool code and conventions only. Vault notes live in `mdsilcox/knowledge-vault-data` (private). Never commit vault content here.
- The vault holds only key, reusable findings, linked back to their source project; per-project memory stays where it is.
- Full rules: `docs/vision.md` (what goes in, writing moments, non-goals).

## Plans and decisions
- Progress and phase plans: Orchestra board (https://claude.ai/artifact/Eqis6DgyZMefwhzFM1KNta), project id `knowledge-vault`, phase prefix `kv~`.
- Decisions: `docs/decisions.md`. A forced change updates the spec and the decision log in the same commit.
