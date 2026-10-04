"""PostToolUse hook: project links, hubs, check, commit, push. Spec: docs/spec/02-sync-hook.md."""
import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from kv.check import check_vault
from kv.hubs import ensure_project_links, update_hubs

MATCHER = r"mcp__basic-memory__(write_note|edit_note|move_note|delete_note)"
VERBS = {"write_note": "created", "edit_note": "updated", "move_note": "moved", "delete_note": "deleted"}


@dataclass
class SyncResult:
    committed: bool = False
    pushed: bool = False
    blocked: bool = False
    message: str = ""
    warnings: list[str] = field(default_factory=list)


def _git(vault: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=vault, capture_output=True, text=True)


def _changed_files(vault: Path) -> set[Path]:
    out = _git(vault, "status", "--porcelain", "-z", "--untracked-files=all").stdout
    entries = out.split("\0")
    changed, i = set(), 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        changed.add((vault / entry[3:]).resolve())
        if entry[0] in "RC":
            i += 1  # skip the original path
    return changed


def _ahead(vault: Path) -> bool:
    r = _git(vault, "rev-list", "--count", "@{u}..HEAD")
    return r.returncode == 0 and r.stdout.strip() not in ("", "0")


def _push(vault: Path) -> bool:
    if _git(vault, "push").returncode == 0:
        return True
    if _git(vault, "pull", "--rebase").returncode != 0:
        _git(vault, "rebase", "--abort")
        return False
    return _git(vault, "push").returncode == 0


def handle_hook(payload: dict, vault: Path) -> SyncResult:
    vault = Path(vault)
    result = SyncResult()
    tool = str(payload.get("tool_name", ""))
    if not re.fullmatch(MATCHER, tool):
        return result
    ensure_project_links(vault)
    update_hubs(vault)
    changed = _changed_files(vault)
    problems = [p for p in check_vault(vault) if p.path.resolve() in changed]
    secrets = [p for p in problems if p.code == "secret"]
    if secrets:
        lines = [f"{p.path.relative_to(vault).as_posix()}: {p.message.removeprefix('Possible secret: ')}"
                 for p in secrets]
        result.blocked = True
        result.message = ("Nothing was committed: possible secrets found. Remove them from these "
                          "notes, then write again.\n" + "\n".join(lines))
        return result
    result.warnings = [f"{p.code} {p.path.relative_to(vault).as_posix()}: {p.message}" for p in problems]

    _git(vault, "add", "-A")
    if _git(vault, "diff", "--cached", "--quiet").returncode == 1:
        inputs = payload.get("tool_input") or {}
        title = inputs.get("title") or str(inputs.get("identifier") or "").rsplit("/", 1)[-1]
        verb = VERBS[tool.rsplit("__", 1)[1]]
        c = _git(vault, "commit", "-q", "-m", f"vault: {verb} {title}".strip())
        if c.returncode != 0:
            result.message = f"Could not commit: {(c.stderr or c.stdout).strip()}"
            return result
        result.committed = True
    if result.committed or _ahead(vault):
        result.pushed = _push(vault)
        if not result.pushed:
            result.message = ("Could not reach the remote. The note is saved locally and will be "
                              "pushed with the next write.")
    else:
        result.pushed = True  # nothing to push
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="kv sync")
    parser.add_argument("--vault", required=True)
    args = parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}
    result = handle_hook(payload, Path(args.vault))
    if not result.blocked and result.pushed and not result.warnings:
        return 0
    parts = [result.message, *result.warnings]
    print("\n".join(p for p in parts if p), file=sys.stderr)
    return 2
