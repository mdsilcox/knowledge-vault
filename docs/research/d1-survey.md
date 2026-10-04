# D1 survey: existing tools (2026-10-04)

Researcher report, checked by the orchestrator against current docs (Context7) where marked. Tags: **[V]** verified in docs or repo, **[S]** search summary only, **[I]** inferred.

## Vault and memory MCP servers
| Tool | Fit | Notes |
|---|---|---|
| **basic-memory** (basicmachines-co) | strong | [V] Plain Markdown with YAML frontmatter (`title`, `type`, `tags`, `permalink`, any custom fields). Observations (`- [decision] ...`) and relations (`[[Other Note]]`) are optional and parsed anywhere in the body. Works without Obsidian. Read, write, edit, move, delete, search, graph tools. Hybrid full-text plus vector search: FastEmbed `bge-small-en-v1.5` locally, vectors in sqlite-vec, no API key. Index is one SQLite file in `~/.basic-memory/memory.db` (or `BASIC_MEMORY_CONFIG_DIR`), outside the vault, rebuildable with `bm reindex --embeddings`. AGPL-3.0 (fine for personal use). Has a paid cloud tier; local use is free. |
| mcp-markdown-vault (wirux) | unproven | [S] Headless, hybrid vector plus TF-IDF, local embeddings. Maintenance and Windows behavior unchecked. |
| vault-mcp (cxrobx) | weaker | [S] SQLite FTS5 plus numpy vectors, but needs Ollama running. |
| smart-connections-mcp | weak | [S] Read-only; reuses the Smart Connections plugin index, which only updates while Obsidian is open. |
| Local REST API servers (mcp-obsidian variants) | no | Need Obsidian running. |
| Official MCP memory server | no | [I] JSON knowledge graph, not Markdown, no semantic search. |

## Free local semantic search on Windows
- **FastEmbed** (ONNX, no PyTorch): `bge-small-en-v1.5`, tens of MB, fast on CPU. [S] for speed figures.
- **model2vec**: static ~30 MB models, much faster, small quality drop. [S]
- Storage: for a few thousand notes, sqlite-vec plus FTS5 in one file, or plain numpy, is plenty. [I]

## iPhone sync over git (the weakest link)
- **Obsidian Git plugin on iOS**: [V/S] isomorphic-git, HTTPS token only, memory-limited, the plugin's own docs call mobile "very unstable", no background sync.
- **Working Copy**: free tier cannot push; Pro is paid. Rejected (not free).
- **GitSync**: [S] native git, free to download with optional paid extras. Unverified.
- Recommended pattern: keep the vault small and text-only (index outside it), the PC commits and pushes, the phone mostly reads with a manual pull, a fine-grained token scoped to the one repo, and test a clone on the real phone early.

## Claude Code memory today
- [V] CLAUDE.md is loaded every session; auto memory (per repo, `MEMORY.md` index, first 200 lines or 25 KB loaded) is written by Claude.
- [V] MCP tool search is on by default for current models: tool definitions are deferred and servers connect lazily, so a server's tool count barely affects per-session cost.
- Division of labor: auto memory keeps small per-repo habits; the vault keeps cross-project findings, searched on demand; one line in the global CLAUDE.md says when to search or write it.

## Sources
- https://github.com/basicmachines-co/basic-memory (and docs.basicmemory.com, via Context7)
- https://github.com/wirux/mcp-markdown-vault, https://github.com/cxrobx/vault-mcp, https://github.com/msdanyg/smart-connections-mcp
- https://publish.obsidian.md/git-doc/Getting+Started
- https://www.stephanmiller.com/obsidian-git-sync-mobile/
- https://code.claude.com/docs/en/memory, https://code.claude.com/docs/en/mcp
