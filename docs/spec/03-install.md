# 3. Install and registration

One command sets up the PC: `uv run python -m kv install` (with `--dry-run` to print the plan without changing anything).

## Steps
1. `uv tool install basic-memory` (Python 3.12+ from uv). If uv's minor-version link error appears (see `docs/spike.md`), retry with `--python <path to uv's python.exe>`.
2. Clone `https://github.com/mdsilcox/knowledge-vault-data.git` to `E:\Backup Desktop\Claude Code Projects\knowledge-vault-data` if it isn't there; copy the `vault-seed/` files (README, `.gitattributes`, `.gitignore`) into it when missing; commit and push them.
3. basic-memory: `bm project add vault <path>`, `bm project default vault`, `semantic_search_enabled true`, provider `fastembed`; `bm reindex`.
4. MCP server at user scope: `claude mcp add basic-memory -s user -e PYTHONUTF8=1 -e PYTHONIOENCODING=utf-8 -- basic-memory mcp`.
5. Hook: merge the `PostToolUse` entry into `~/.claude/settings.json`.
6. Skill: copy `skill/SKILL.md` to `~/.claude/skills/vault/SKILL.md`.
7. Global CLAUDE.md: add a short "Knowledge vault" section (when to search, when to write, use the vault skill).
8. Print what was done and what the owner must do next (restart Claude Code sessions to load the server).

## Rules
- **Never overwrite the owner's data.** Settings and CLAUDE.md are merged, never replaced: existing hooks, keys and text stay exactly as they were. A backup (`settings.json.bak-<date>`) is written before the first change.
- **Idempotent:** running install again changes nothing and says so.
- Each step reports done, already done, or failed with the reason; a failure stops the steps that depend on it.

## Acceptance criteria
- **Given** settings with an existing `PreToolUse` Bash hook, **when** merged, **then** that hook is unchanged and a `PostToolUse` entry with the vault matcher is added.
- **Given** settings that already contain the vault hook, **when** merged, **then** the result equals the input (no duplicate).
- **Given** settings with other top-level keys (theme, plugins), **then** they are preserved exactly.
- **Given** a CLAUDE.md without the section, **then** it is appended once at the end; **given** one that has it, **then** the text is unchanged.
- **Given** `--dry-run`, **then** no file is touched and the plan lists every step.
- Live check at the Build gate: a new Claude Code session in another project lists the `basic-memory` server and can call `search_notes`.
