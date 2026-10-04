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
- **Confirmed** by the spike (docs/spike.md), 2026-10-04.

## 2026-10-04: Runtime and install
- **Chosen:** uv (installed globally by the user) provides Python 3.12+ and installs basic-memory as a tool. System Python stays 3.11.
- **Why:** basic-memory needs Python 3.12+; uv is its recommended installer and keeps the install in a short path (Windows path-length limit broke an install in a deep folder).

## 2026-10-04: Search mode
- **Chosen:** basic-memory's default hybrid search (full text plus FastEmbed `bge-small-en-v1.5` vectors in sqlite-vec).
- **Rejected:** vector-only (missed 1 of 4 reworded questions in the spike, under its 0.55 similarity cutoff).

## 2026-10-04: Phone sync
- **Chosen:** free Obsidian plus the free Obsidian Git plugin on the iPhone, cloning the private repo into a `vault` subfolder; the phone reads and pulls, the PC writes and pushes.
- **Rejected:** Working Copy (pushing needs the paid tier); iCloud (fights with git, and the PC would need iCloud for Windows); GitSync (not needed, Obsidian Git worked).
- **Why:** proved end to end in the spike: clone, pull, wikilinks and graph view all work.

## 2026-10-04: Search filter for problem questions (Build 1)
- **Chosen:** the vault skill searches with `note_types` limited to pattern, finding, decision, research and note; project questions read the hub directly. The vault README gets `type: readme`.
- **Rejected:** excluding hubs from the index (they are useful for project overviews and the graph); vector-only search (missed a reworded question in the spike).
- **Why:** in the live test the hub and README outranked the real note in hybrid search. See docs/retro/b1.md.

## 2026-10-04: Secret block scope (Build 1)
- **Chosen:** the sync hook blocks a commit only for secrets in files changed by the current write.
- **Rejected:** blocking on any secret anywhere in the vault (one old secret would block every later write).

## 2026-10-04: Read the top 3-5 search results, not only the first (Build 2)
- **Chosen:** keep basic-memory's default hybrid search; the skill scans the top 3-5 titles and reads the one or two that fit. The gate measures untuned questions as "fitting note in the top 3, at least 4 of 5".
- **Rejected:** switching to vector-only (2 of 5 first, 5 of 5 in the top 3, against hybrid's 3 of 5 first and 4 of 5 in the top 3 on the same untuned questions: no clear winner); a bigger embedding model (possible later if ranking stays weak as the vault grows).
- **Why:** with 28 notes, five questions written without looking at results put the right note first only 3 times out of 5 in hybrid mode. Broad notes (the survey, decisions) collect matches. Claude can judge from titles, so reading a few results costs little.
