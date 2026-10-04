"""Spec: docs/spec/06-seed.md. Gate checks against the real seeded vault: KV_GATE_VAULT=<path> uv run pytest -m gate"""
import os
from pathlib import Path

import pytest

from kv.check import check_vault
from kv.hubs import END, START
from kv.notes import parse_note

pytestmark = pytest.mark.gate

REPO = Path(__file__).resolve().parents[1]
VAULT = Path(os.environ["KV_GATE_VAULT"]) if os.environ.get("KV_GATE_VAULT") else None

# Filled in when the seed notes are written in Build: (reworded question, expected pattern title), three entries.
PATTERN_QUESTIONS: list[tuple[str, str]] = [
    ("installing a heavy Python library from a long directory path on Windows leaves broken modules",
     "Windows path length breaks Python installs in deep folders"),
    ("cloning a repository into the vault root in Obsidian on iOS fails",
     "Clone Obsidian Git into a subfolder on iOS"),
    ("before the review gate, try the real integration once because the test suite missed defects",
     "Run one live write through the real tools before the gate review"),
]


@pytest.fixture
def vault() -> Path:
    if VAULT is None:
        pytest.skip("KV_GATE_VAULT is not set")
    assert VAULT is not None
    return VAULT


def seeded(vault: Path):
    notes = [parse_note(p) for p in vault.rglob("*.md")
             if not any(part.startswith((".", "_")) for part in p.relative_to(vault).parts)
             and p.parent != vault]
    return [n for n in notes if n.frontmatter.get("project") == "knowledge-vault"]


def test_no_errors(vault):
    assert [p for p in check_vault(vault) if p.severity == "error"] == []


def test_hub_lists_every_note_and_types_are_covered(vault):
    notes = seeded(vault)
    hub = (vault / "projects" / "knowledge-vault.md").read_text(encoding="utf-8")
    listed = hub.split(START, 1)[1].split(END, 1)[0]
    others = [n for n in notes if n.frontmatter["type"] != "project"]
    for n in others:
        assert f"[[{n.title}]]" in listed, n.title
    assert {"pattern", "finding", "decision", "research"} <= {n.frontmatter["type"] for n in others}


def test_every_note_has_a_source_in_this_repo(vault):
    for n in seeded(vault):
        if n.frontmatter["type"] == "project":
            continue
        source = n.frontmatter.get("source", "")
        assert source and (REPO / source).exists(), (n.title, source)


# Written by the orchestrator without looking at results first (the PATTERN_QUESTIONS above were
# reworded by the seed lane until they ranked first, so they overstate quality). Each expected title
# should appear in the top 3, matching the skill's "scan the top 3-5 titles"; 4 of 5 is the bar.
UNTUNED_QUESTIONS: list[tuple[str, set[str]]] = [
    ("my phone app crashes when downloading a big git repository",
     {"Obsidian Git is unstable on iOS but fine read-mostly", "Sync the phone with free Obsidian Git, read-only"}),
    ("how much context does the memory server cost if I never use it",
     {"MCP tool search defers tool definitions", "basic-memory costs about 3,000 tokens on first use per session"}),
    ("should two agents work on the same module at the same time",
     {"Split agent lanes by coupling, not by file list"}),
    ("we rebuilt something an earlier experiment had already built",
     {"Reuse existing working code before rebuilding it with an agent"}),
    ("can I delete the database file without losing notes",
     {"basic-memory index lives outside the vault and rebuilds losslessly"}),
]


def _top_titles(bm: str, question: str, n: int) -> list[str]:
    import json
    import subprocess
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    types = [arg for t in ("pattern", "finding", "decision", "research", "note") for arg in ("--type", t)]
    out = subprocess.run([bm, "tool", "search-notes", question, "--json", "--page-size", str(n), *types],
                         env=env, capture_output=True, text=True, check=True).stdout
    return [r["title"] for r in json.loads(out)["results"]]


def test_untuned_questions_find_notes_in_top_three(vault):
    import shutil
    bm = shutil.which("basic-memory")
    if not bm:
        pytest.skip("basic-memory is not installed")
    hits = [q for q, expected in UNTUNED_QUESTIONS if expected & set(_top_titles(bm, q, 3))]
    assert len(hits) >= 4, f"only {len(hits)} of {len(UNTUNED_QUESTIONS)} in the top 3: {hits}"


def test_pattern_questions_are_defined():
    assert len(PATTERN_QUESTIONS) == 3, "add three reworded questions when seeding"


def test_reworded_questions_find_seeded_patterns(vault):
    import json
    import shutil
    import subprocess
    bm = shutil.which("basic-memory")
    if not bm:
        pytest.skip("basic-memory is not installed")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    for question, expected in PATTERN_QUESTIONS:
        types = [arg for t in ("pattern", "finding", "decision", "research", "note") for arg in ("--type", t)]
        out = subprocess.run([bm, "tool", "search-notes", question, "--json", "--page-size", "3", *types],
                             env=env, capture_output=True, text=True, check=True).stdout
        results = json.loads(out)["results"]
        assert results and results[0]["title"] == expected, question
