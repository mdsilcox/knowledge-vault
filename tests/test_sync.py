"""Spec: docs/spec/02-sync-hook.md."""
import json
import subprocess
import sys

from kv.sync import handle_hook
from tests.conftest import git, payload, remote_log, write_note


def test_write_note_commits_and_pushes(synced_vault):
    vault, remote = synced_vault
    write_note(vault, "New finding", link_hub=False)
    result = handle_hook(payload("write_note", "New finding"), vault)
    assert result.committed and result.pushed and not result.blocked
    assert remote_log(remote)[0] == "vault: created New finding"
    files = git(remote, "show", "--name-only", "--format=", "main").splitlines()
    assert "findings/New finding.md" in files
    assert "projects/demo.md" in files
    note = git(remote, "show", "main:findings/New finding.md")
    assert "Project: [[demo]]" in note


def test_edit_note_says_updated(synced_vault):
    vault, remote = synced_vault
    path = write_note(vault, "Some finding")
    handle_hook(payload("write_note", "Some finding"), vault)
    path.write_text(path.read_text(encoding="utf-8") + "\nMore evidence.\n", encoding="utf-8")
    handle_hook(payload("edit_note", identifier="Some finding"), vault)
    assert remote_log(remote)[0] == "vault: updated Some finding"


def test_other_tools_are_ignored(synced_vault):
    vault, remote = synced_vault
    write_note(vault, "Unrelated change")
    p = payload("write_note", "x")
    p["tool_name"] = "mcp__github__search"
    result = handle_hook(p, vault)
    assert not result.committed
    assert remote_log(remote) == ["init"]


def test_no_empty_commit(synced_vault):
    vault, remote = synced_vault
    result = handle_hook(payload("edit_note", identifier="demo"), vault)
    assert not result.committed
    assert remote_log(remote) == ["init"]


def test_secret_blocks_commit(synced_vault):
    vault, remote = synced_vault
    write_note(vault, "Leaky", body="token ghp_" + "A1b2" * 9)
    result = handle_hook(payload("write_note", "Leaky"), vault)
    assert result.blocked and not result.committed
    assert "Leaky" in result.message and "GitHub token" in result.message
    assert remote_log(remote) == ["init"]
    assert git(vault, "log", "--format=%s") == "init"


def test_rejected_push_rebases_and_retries(synced_vault, tmp_path):
    vault, remote = synced_vault
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(remote), str(other))
    git(other, "config", "user.name", "Other")
    git(other, "config", "user.email", "other@example.com")
    write_note(other, "From elsewhere")
    git(other, "add", "-A")
    git(other, "commit", "-q", "-m", "elsewhere")
    git(other, "push", "-q")
    write_note(vault, "Local finding")
    result = handle_hook(payload("write_note", "Local finding"), vault)
    assert result.pushed
    log = remote_log(remote)
    assert "elsewhere" in log and "vault: created Local finding" in log


def test_offline_keeps_commit_and_pushes_next_time(synced_vault, tmp_path):
    vault, remote = synced_vault
    moved = tmp_path / "remote-away.git"
    remote.rename(moved)
    write_note(vault, "Offline finding")
    result = handle_hook(payload("write_note", "Offline finding"), vault)
    assert result.committed and not result.pushed
    assert "next" in result.message.lower()
    moved.rename(remote)
    write_note(vault, "Online finding")
    result = handle_hook(payload("write_note", "Online finding"), vault)
    assert result.pushed
    log = remote_log(remote)
    assert "vault: created Offline finding" in log and "vault: created Online finding" in log


def test_idempotent(synced_vault):
    vault, remote = synced_vault
    write_note(vault, "Once")
    handle_hook(payload("write_note", "Once"), vault)
    second = handle_hook(payload("write_note", "Once"), vault)
    assert not second.committed
    assert remote_log(remote).count("vault: created Once") == 1


def test_main_exit_codes(synced_vault):
    vault, _ = synced_vault

    def run(p):
        return subprocess.run([sys.executable, "-m", "kv", "sync", "--vault", str(vault)],
                              input=json.dumps(p), capture_output=True, text=True)

    write_note(vault, "Clean one")
    assert run(payload("write_note", "Clean one")).returncode == 0
    write_note(vault, "Leaky", body="ghp_" + "A1b2" * 9)
    blocked = run(payload("write_note", "Leaky"))
    assert blocked.returncode == 2
    assert "GitHub token" in blocked.stderr
