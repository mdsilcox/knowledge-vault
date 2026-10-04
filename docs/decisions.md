# Decision log

One entry per decision: what was chosen, what was rejected, and why. Newest last.

## 2026-10-04: Project track
- **Chosen:** Medium track (the user's pick on the board, 2026-10-04).
- **Rejected:** Small (would skip the spike of the Claude read/write bridge, the piece most likely to change the design); Large (five separately approved discovery phases is more ceremony than a single-user tool needs).
- **Shape:** D1 ideation plus tech stack with a spike; D2 data model plus spec and roadmap; then build phases.
- **GitHub:** github.com/mdsilcox/knowledge-vault (exists, public, empty). Whether vault content lives in this repo or a separate private one is open in D1.

## 2026-10-04: Vision approved
- docs/vision.md approved by the user on the board.

## 2026-10-04: How Claude reads and writes the vault
- **Chosen:** adopt basic-memory as a user-level MCP server pointed at the vault folder (the user's pick in chat; the board's option picker was locked once the phase was active). This repo holds conventions (templates, layout, a skill, sync scripts), not a server.
- **Rejected:** a custom Python MCP server (more to build and maintain; kept as the fallback if the spike fails a must-have); mcp-markdown-vault and vault-mcp (young, unverified on Windows, vault-mcp needs Ollama running); Smart Connections MCP (index updates only with Obsidian open); Local REST API servers (need Obsidian running).
- **Why:** basic-memory already covers plain Markdown, free local hybrid search (FastEmbed plus sqlite-vec) and read/write tools, and keeps its index outside the vault. See docs/research/d1-survey.md.
- **Pending:** confirmed by the spike (docs/spike.md).
