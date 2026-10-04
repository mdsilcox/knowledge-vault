"""The 15-note vault from the D1 spike (docs/spike.md), as (folder, title, type, tags, body)."""
from pathlib import Path

NOTES = [
    ("decisions", "Adopt basic-memory for the vault", "decision", ["mcp"], "Chose basic-memory over a custom Python MCP server for Claude's vault access. It already gives plain Markdown, local hybrid search (FastEmbed plus sqlite-vec) and read/write tools, with the index outside the vault. Custom server kept as fallback. Related: [[FastEmbed runs locally on CPU]]."),
    ("decisions", "Tool code public, notes private", "decision", ["git"], "Two repos: the public repo holds tool code and conventions, a private repo holds the notes. Research and project details should not be world-readable. Private GitHub repos are free."),
    ("findings", "Obsidian Git is unstable on iOS", "finding", ["obsidian", "ios", "sync"], "The Obsidian Git plugin uses isomorphic-git on mobile: HTTPS token only, memory-limited, can crash on big clones, no background sync. Its own docs call mobile very unstable. Use the phone read-mostly and keep the repo small. See [[Working Copy is not free for pushing]]."),
    ("findings", "Working Copy is not free for pushing", "finding", ["ios", "sync"], "Working Copy, the popular iOS git client, cannot push on the free tier; Pro costs about 36 dollars. GitSync is a free alternative with native git."),
    ("patterns", "Windows path length breaks Python installs", "pattern", ["windows", "python"], "Problem: a package installs without errors but importing it fails with ModuleNotFoundError for a deeply nested module. Cause: the 260 character MAX_PATH limit on Windows silently truncates files when the virtual environment lives in a long folder such as a temp scratchpad. Fix: create the venv in a short path like C:/Users/<you>/proj."),
    ("patterns", "uv python minor version link error", "pattern", ["windows", "python", "uv"], "Problem: uv venv --python 3.12 fails with 'Missing expected target directory for Python minor version link'. The download succeeded but uv could not create the minor-version junction. Workaround: pass the full path to the downloaded python.exe under AppData/Roaming/uv/python."),
    ("findings", "MCP tool search defers tool definitions", "finding", ["claude-code", "mcp", "tokens"], "Claude Code loads MCP tool definitions lazily through tool search for current models, so a server with many tools adds little fixed cost per session. Disabled with a custom ANTHROPIC_BASE_URL or older models."),
    ("findings", "Auto memory index load limit", "finding", ["claude-code", "memory"], "Claude Code auto memory loads only the first 200 lines or 25 KB of MEMORY.md at session start; keep the index to one line per memory."),
    ("findings", "Board option picker locks when phase is active", "finding", ["orchestra"], "On the Orchestra board, a step's options cannot be picked once its phase is active. Put choices in a draft phase, or take the user's pick in chat."),
    ("patterns", "Do not parallelize sequential work", "pattern", ["orchestration", "agents"], "Multi-agent setups gain on work that splits cleanly but lose 39 to 70 percent on sequential tasks. Give a chain of dependent steps to one agent. Three or four lanes is the usual sweet spot."),
    ("patterns", "Split lanes by coupling", "pattern", ["orchestration", "agents"], "Group tightly coupled files under one agent rather than splitting by file list; cross-agent merge conflicts run about twice the single-agent rate. Build shared interfaces as contracts first. See [[Do not parallelize sequential work]]."),
    ("patterns", "Spike the riskiest piece before choosing a stack", "pattern", ["process"], "The stack is the most expensive decision to undo. Build a throwaway spike of the riskiest technical piece before committing."),
    ("findings", "Git Bash mangles non-ASCII arguments", "finding", ["windows", "bash"], "In Git Bash on Windows, non-ASCII text in command-line arguments (curl, sqlite) can arrive as question marks. Send such data from a Python script run with PYTHONUTF8=1."),
    ("findings", "FastEmbed runs locally on CPU", "finding", ["embeddings", "search"], "FastEmbed uses ONNX without PyTorch; bge-small-en-v1.5 is tens of MB and fast on CPU, no API key. Good default for free local semantic search."),
    ("findings", "Smart Connections index needs Obsidian open", "finding", ["obsidian", "search"], "The Smart Connections plugin's embeddings only update while Obsidian is running, so agents reading its index see stale results. Not suitable as the agents' search backend."),
]

# (question, expected top title): reworded on purpose, from the spike.
QUESTIONS = [
    ("pip package imports fail with module not found inside a deep temp folder", "Windows path length breaks Python installs"),
    ("how do I sync my notes to my phone for free", "Obsidian Git is unstable on iOS"),
    ("should I run several agents at once for a step-by-step task", "Do not parallelize sequential work"),
    ("unicode characters turn into question marks in shell commands", "Git Bash mangles non-ASCII arguments"),
]


def build(vault: Path) -> None:
    for folder, title, type_, tags, body in NOTES:
        path = vault / folder / f"{title}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\ntitle: {title}\ntype: {type_}\ntags: [{', '.join(tags)}]\nproject: knowledge-vault\n"
            f"created: 2026-10-04\nstatus: active\n---\n\n# {title}\n\n{body}\n",
            encoding="utf-8", newline="\n")
