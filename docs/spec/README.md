# Specs

**Status:** draft for approval (Discovery 2, 2026-10-04). Built on `docs/vision.md` and `docs/data-model.md`.

| # | Feature | Spec | Acceptance tests |
|---|---|---|---|
| 1 | Vault checker (invariants) | [01-checker.md](01-checker.md) | `tests/test_check.py`, `tests/test_secrets.py` |
| 2 | Sync hook (project links, hubs, commit, push) | [02-sync-hook.md](02-sync-hook.md) | `tests/test_hubs.py`, `tests/test_sync.py` |
| 3 | Install and registration | [03-install.md](03-install.md) | `tests/test_install.py` |
| 4 | Search through basic-memory | [04-search.md](04-search.md) | `tests/test_search_e2e.py` (slow) |
| 5 | The vault skill (when and how Claude uses it) | [05-skill.md](05-skill.md) | scenario checks in a live session |
| 6 | Seeding with this project's findings | [06-seed.md](06-seed.md) | `tests/test_seed.py` (gate) |
| 7 | User guide | [07-user-guide.md](07-user-guide.md) | review checklist |

## Code contract (what the tests import)
A small Python package `kv` in this repo (Python 3.12+, run with uv; dev deps pytest and PyYAML). It is glue around basic-memory, not a server.

```
kv/
  notes.py     parse_note(path) -> Note(path, frontmatter: dict, body: str, title: str)
               wikilinks(text) -> list[str]      # targets, with |alias and #heading stripped
  secrets.py   find_secrets(text) -> list[str]   # names of matched patterns, empty if clean
  check.py     check_vault(vault: Path) -> list[Problem]
               Problem(code: str, path: Path, message: str, severity: "error" | "warning")
  hubs.py      ensure_project_links(vault) -> list[Path]   # notes changed
               update_hubs(vault) -> list[Path]            # hubs created or changed
  sync.py      handle_hook(payload: dict, vault: Path) -> SyncResult
               SyncResult(committed: bool, pushed: bool, blocked: bool, message: str, warnings: list[str])
               main()  # reads the hook payload from stdin; exit 0 when clean, exit 2 with stderr for Claude otherwise
  install.py   merge_settings(settings: dict, hook_command: str) -> dict
               merge_claude_md(text: str) -> str
               main(argv)  # kv install [--dry-run]
  __main__.py  python -m kv check <vault> | sync --vault <vault> | install [--dry-run]
templates/     one Markdown template per note type
skill/SKILL.md the vault skill, copied to ~/.claude/skills/vault/
vault-seed/    README.md, .gitattributes, .gitignore for the data repo
```

## Test conventions
- Every test works on a throwaway vault in `tmp_path`, with a bare git repo in `tmp_path` as the "GitHub" remote. Never the real vault, never the network.
- basic-memory runs only in tests marked `slow`, with `BASIC_MEMORY_CONFIG_DIR` in `tmp_path`; they skip when basic-memory is not installed.
- Run: `uv run pytest` (fast) and `uv run pytest -m slow` (end to end).
