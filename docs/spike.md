# Spike: basic-memory as the vault server (2026-10-04)

Throwaway setup in `C:\Users\mikha\kvspike` (deleted after the spike): basic-memory 0.23.2 in a uv-made Python 3.12.15 venv, config and index in a scratch `BASIC_MEMORY_CONFIG_DIR`, a scratch vault of 15 notes written from this project's real findings. The real `~/.basic-memory` was never touched.

## Results (PC)
| Check | Result |
|---|---|
| Install on Windows | Works. 358 MB venv (includes the ONNX runtime). Needs Python 3.12+; system Python is 3.11, so uv provides it. |
| Index 15 notes plus embeddings | ~8 s first run, ~7.5 s full rebuild. Index is a 2 MB SQLite file outside the vault. |
| Search by meaning (default hybrid mode) | 4 of 4 reworded questions put the right note first, e.g. "pip package imports fail with module not found inside a deep temp folder" found "Windows path length breaks Python installs". |
| Vector-only mode | 3 of 4: the phone-sync question fell under the 0.55 similarity cutoff. Use the default hybrid mode. |
| Write a note | `write_note` makes a clean Obsidian note: YAML frontmatter (`title`, `type`, `tags`, `permalink`), body as given, wikilinks intact. |
| Delete index, rebuild from files | Nothing lost: same search answers, note files unchanged by the rebuild. |
| Live Claude Code session through MCP | Not run: the headless `claude` CLI's login had expired. Replaced by a direct MCP client probe (below). Live test moves to Build 1, when the server is installed for real. |

## Token cost (MCP probe; estimates at ~4 characters per token)
- **Fixed cost per session, vault unused:** ~300 tokens (server instructions ~211, plus 21 deferred tool names ~72). Claude Code's tool search keeps the full definitions out until needed.
- **First use in a session:** loading the schemas for `search_notes` (~1,100), `read_note` (~600) and `write_note` (~900), plus one search result (~400) and one note (~125): roughly **3,000 tokens**. Later queries in the same session: ~400-600 each.
- **Without tool search** (older models, custom API base URL) all 21 definitions would load every session: ~11,000 tokens. Worth knowing; not our setup.

## Gotchas found
1. **Python 3.12+ required.** Install with uv.
2. **Windows path length:** installing into a long folder (the temp scratchpad) silently truncated files and broke imports. Keep the install path short; `uv tool install` puts it in a short path anyway.
3. **uv minor-version link error** (`Missing expected target directory for Python minor version link`): uv could not create its junction here. Workaround: point `uv venv --python` at the downloaded `python.exe` directly. Check whether `uv tool install` hits the same thing in Build 1.
4. **CLI needs a UTF-8 console:** `bm` crashed on its spinner character in the Windows console. Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` (also set in the MCP server's env).
5. **basic-memory edits notes on sync:** it adds a `permalink` field and rewrites `tags` into block style in existing notes (`ensure_frontmatter_on_sync: true`). Harmless for Obsidian, but it means the files change after Claude or the owner writes them. Decide in D2 whether to keep it or turn it off.
6. **Line endings:** git on this PC converts LF to CRLF. The data repo should carry a `.gitattributes` with `* text=auto eol=lf` so the PC and the phone agree.
7. **21 tools** include project, workspace and schema management that we don't need. Fine with tool search; a skill should steer Claude to the four that matter (search, read, write, edit).

## Results (iPhone)
TODO: clone `knowledge-vault-data` in Obsidian with the Obsidian Git plugin, pull the `_spike` test notes, check the graph view.

## Verdict
TODO after the iPhone test. PC side: basic-memory meets every PC must-have in the vision; no reason to fall back to a custom server.
