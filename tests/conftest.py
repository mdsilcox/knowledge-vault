"""Shared fixtures: throwaway vaults and a bare git repo standing in for GitHub."""
import subprocess
from pathlib import Path

import pytest
import yaml

FOLDERS = {
    "pattern": "patterns",
    "finding": "findings",
    "decision": "decisions",
    "research": "research",
    "note": "notes",
    "project": "projects",
}


def write_note(vault: Path, title: str, type_: str = "finding", project: str = "demo",
               body: str = "", folder: str | None = None, link_hub: bool = True, **fields) -> Path:
    """Write a note that follows the data model unless fields override it (None removes a field)."""
    fm = {"title": title, "type": type_, "project": project, "tags": ["demo"],
          "created": "2026-10-04", "status": "active"}
    fm.update(fields)
    fm = {k: v for k, v in fm.items() if v is not None}
    if type_ != "project" and link_hub and f"[[{project}]]" not in body:
        body = f"{body}\n\nProject: [[{project}]]"
    path = vault / (folder or FOLDERS.get(type_, "notes")) / f"{title}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n# {title}\n{body}\n",
                    encoding="utf-8", newline="\n")
    return path


def write_hub(vault: Path, project: str = "demo", extra: str = "") -> Path:
    return write_note(vault, project, type_="project", project=project,
                      body=f"{extra}\n<!-- kv:notes -->\n<!-- /kv:notes -->", repo="local")


@pytest.fixture
def good_vault(tmp_path: Path) -> Path:
    """A small vault that satisfies every invariant."""
    vault = tmp_path / "vault"
    write_hub(vault)
    write_note(vault, "Alpha finding", body="Links to [[Beta pattern]].")
    write_note(vault, "Beta pattern", type_="pattern", body="See [[Alpha finding|the finding]].")
    write_note(vault, "Gamma decision", type_="decision", body="See [[Beta pattern#Solution]].")
    (vault / "README.md").write_text("# Vault\nNo frontmatter here, and that is fine.\n", encoding="utf-8")
    (vault / ".obsidian").mkdir()
    (vault / ".obsidian" / "junk.md").write_text("not a note", encoding="utf-8")
    return vault


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def synced_vault(tmp_path: Path) -> tuple[Path, Path]:
    """(vault clone, bare remote) with one initial commit pushed."""
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    vault = tmp_path / "vault"
    git(tmp_path, "clone", "-q", str(remote), str(vault))
    git(vault, "config", "user.name", "Test")
    git(vault, "config", "user.email", "test@example.com")
    git(vault, "config", "core.autocrlf", "false")
    write_hub(vault)
    git(vault, "add", "-A")
    git(vault, "commit", "-q", "-m", "init")
    git(vault, "push", "-q", "-u", "origin", "main")
    return vault, remote


def remote_log(remote: Path) -> list[str]:
    return git(remote, "log", "--format=%s", "main").splitlines()


def payload(tool: str, title: str = "", identifier: str = "") -> dict:
    tool_input = {"title": title, "directory": "findings", "content": "x"} if title else {"identifier": identifier}
    return {"hook_event_name": "PostToolUse", "tool_name": f"mcp__basic-memory__{tool}",
            "tool_input": tool_input, "tool_response": {}, "cwd": "."}
