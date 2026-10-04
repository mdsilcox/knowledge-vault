"""Spec: docs/spec/03-install.md."""
import copy
import subprocess
import sys

from kv.install import CLAUDE_MD_HEADING, merge_claude_md, merge_settings
from kv.sync import MATCHER

HOOK = '"C:/repo/.venv/Scripts/python.exe" -m kv sync --vault "E:/vault"'

EXISTING = {
    "theme": "dark",
    "enabledPlugins": {"pyright-lsp": True},
    "hooks": {
        "PreToolUse": [{
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": "python quiet_tests_hook.py", "timeout": 10}],
        }]
    },
}


def test_merge_keeps_existing_hooks_and_adds_ours():
    original = copy.deepcopy(EXISTING)
    merged = merge_settings(copy.deepcopy(EXISTING), HOOK)
    assert merged["hooks"]["PreToolUse"] == original["hooks"]["PreToolUse"]
    post = merged["hooks"]["PostToolUse"]
    assert len(post) == 1
    assert post[0]["matcher"] == MATCHER
    assert post[0]["hooks"][0]["command"] == HOOK


def test_merge_preserves_other_keys():
    merged = merge_settings(copy.deepcopy(EXISTING), HOOK)
    assert merged["theme"] == "dark"
    assert merged["enabledPlugins"] == {"pyright-lsp": True}


def test_merge_is_idempotent():
    once = merge_settings(copy.deepcopy(EXISTING), HOOK)
    twice = merge_settings(copy.deepcopy(once), HOOK)
    assert twice == once


def test_merge_into_empty_settings():
    merged = merge_settings({}, HOOK)
    assert merged["hooks"]["PostToolUse"][0]["matcher"] == MATCHER


def test_claude_md_section_appended_once():
    text = "# Global instructions\n\nSome rules.\n"
    merged = merge_claude_md(text)
    assert merged.startswith(text)
    assert merged.count(CLAUDE_MD_HEADING) == 1
    assert "vault" in merged[len(text):].lower()
    assert merge_claude_md(merged) == merged


def test_dry_run_lists_every_step_and_touches_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    before = sorted(p.name for p in tmp_path.iterdir())
    result = subprocess.run([sys.executable, "-m", "kv", "install", "--dry-run"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    out = result.stdout.lower()
    for word in ["basic-memory", "clone", "project", "mcp", "hook", "skill", "claude.md"]:
        assert word in out, word
    assert sorted(p.name for p in tmp_path.iterdir()) == before
