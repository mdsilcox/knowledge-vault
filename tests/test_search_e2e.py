"""Spec: docs/spec/04-search.md. Real basic-memory on a throwaway config; run with -m slow."""
import json
import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.fixtures import spike_notes

pytestmark = pytest.mark.slow

BM = shutil.which("basic-memory")


@pytest.fixture
def bm(tmp_path: Path):
    if not BM:
        pytest.skip("basic-memory is not installed")
    vault = tmp_path / "vault"
    spike_notes.build(vault)
    env = dict(os.environ, BASIC_MEMORY_CONFIG_DIR=str(tmp_path / "bmconfig"),
               PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

    def run(*args: str) -> str:
        return subprocess.run([str(BM), *args], env=env, capture_output=True, text=True, check=True,
                              timeout=600).stdout

    run("project", "add", "vault", str(vault))
    run("project", "default", "vault")
    run("config", "set", "semantic_search_enabled", "true")
    run("config", "set", "semantic_embedding_provider", "fastembed")
    run("reindex", "--project", "vault")
    return SimpleNamespace(run=run, vault=vault, config=tmp_path / "bmconfig")


def top_title(bm, question: str) -> str:
    results = json.loads(bm.run("tool", "search-notes", question, "--json", "--page-size", "3"))["results"]
    return results[0]["title"] if results else ""


def snapshot(vault: Path) -> dict:
    return {p: p.read_bytes() for p in vault.rglob("*.md")}


def test_reworded_questions_find_the_right_note(bm):
    for question, expected in spike_notes.QUESTIONS:
        assert top_title(bm, question) == expected, question


def test_write_note_makes_a_clean_file(bm):
    body = "Problem: something.\n\nFix: something else. Related: [[FastEmbed runs locally on CPU]]"
    bm.run("tool", "write-note", "--title", "A new pattern", "--folder", "patterns", "--tags", "windows",
       "--content", body)
    text = (bm.vault / "patterns" / "A new pattern.md").read_text(encoding="utf-8")
    front, rest = text.split("---", 2)[1:]
    for field in ["title:", "type:", "tags:", "permalink:"]:
        assert field in front
    assert body in rest


def test_rebuild_from_files_loses_nothing(bm):
    before = {q: top_title(bm, q) for q, _ in spike_notes.QUESTIONS}
    files = snapshot(bm.vault)
    for db in bm.config.glob("memory.db*"):
        db.unlink()
    bm.run("reindex", "--full", "--project", "vault")
    assert {q: top_title(bm, q) for q, _ in spike_notes.QUESTIONS} == before
    assert snapshot(bm.vault) == files


def test_edit_on_disk_is_found_after_reindex(bm):
    path = bm.vault / "findings" / "FastEmbed runs locally on CPU.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nAlso handles zymurgy glossaries well.\n",
                    encoding="utf-8")
    bm.run("reindex", "--project", "vault")
    assert top_title(bm, "zymurgy") == "FastEmbed runs locally on CPU"
