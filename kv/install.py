"""PC setup: basic-memory, MCP registration, hook, skill, CLAUDE.md. Spec: docs/spec/03-install.md."""
import argparse
import copy
import datetime
import glob
import json
import os
import shutil
import subprocess
from pathlib import Path

from kv.sync import MATCHER

CLAUDE_MD_HEADING = "## Knowledge vault"

REPO = Path(__file__).resolve().parents[1]
VAULT = Path(r"E:\Backup Desktop\Claude Code Projects\knowledge-vault-data")
DATA_REPO_URL = "https://github.com/mdsilcox/knowledge-vault-data.git"


def hook_command_for() -> str:
    python = (REPO / ".venv" / "Scripts" / "python.exe").as_posix()
    return f'"{python}" -m kv sync --vault "{VAULT.as_posix()}"'


def merge_settings(settings: dict, hook_command: str) -> dict:
    merged = copy.deepcopy(settings)
    hooks = merged.setdefault("hooks", {})
    post = hooks.setdefault("PostToolUse", [])
    for entry in post:
        if entry.get("matcher") == MATCHER:
            inner = entry.get("hooks")
            if inner:
                inner[0]["command"] = hook_command
            else:
                entry["hooks"] = [{"type": "command", "command": hook_command, "timeout": 60}]
            return merged
    post.append({"matcher": MATCHER,
                 "hooks": [{"type": "command", "command": hook_command, "timeout": 60}]})
    return merged


def merge_claude_md(text: str) -> str:
    if CLAUDE_MD_HEADING in text:
        return text
    section = (REPO / "skill" / "claude-md-section.md").read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    result = text + ("\n" if text else "") + section
    if not result.endswith("\n"):
        result += "\n"
    return result


# ---- helpers for the real run ----

def _env() -> dict:
    return {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=_env(), cwd=cwd)


def _err(proc: subprocess.CompletedProcess) -> str:
    text = (proc.stderr or proc.stdout or "").strip()
    return text.splitlines()[-1] if text else f"exit code {proc.returncode}"


def _backup(path: Path) -> None:
    if not path.exists():
        return
    bak = path.with_name(f"{path.name}.bak-{datetime.date.today():%Y%m%d}")
    if not bak.exists():
        shutil.copy2(path, bak)


def _report(n: int, step: str, state: str) -> None:
    print(f"[{n}] {step}: {state}")


def _bm() -> str:
    """Path of the basic-memory executable; falls back to uv's tool bin dir (PATH may be stale)."""
    found = shutil.which("basic-memory")
    if found:
        return found
    proc = _run(["uv", "tool", "dir", "--bin"])
    if proc.returncode == 0 and proc.stdout.strip():
        candidate = Path(proc.stdout.strip().splitlines()[-1]) / "basic-memory.exe"
        if candidate.exists():
            return str(candidate)
    return "basic-memory"


def _bm_installed() -> bool:
    if not Path(_bm()).is_absolute():
        return False
    proc = _run(["uv", "tool", "list"])
    return proc.returncode == 0 and "basic-memory" in proc.stdout


def _step_basic_memory() -> str:
    if _bm_installed():
        return "already done"
    proc = _run(["uv", "tool", "install", "basic-memory"])
    if proc.returncode != 0 and "minor version link" in (proc.stderr + proc.stdout):
        appdata = os.environ.get("APPDATA", "")
        found = sorted(glob.glob(os.path.join(appdata, "uv", "python", "cpython-3.12*", "python.exe")))
        if found:
            proc = _run(["uv", "tool", "install", "basic-memory", "--python", found[-1]])
    if proc.returncode != 0:
        return f"failed: {_err(proc)}"
    return "done"


def _step_clone() -> str:
    seed_dir = REPO / "vault-seed"
    state = "already done"
    if not (VAULT / ".git").exists():
        proc = _run(["git", "clone", DATA_REPO_URL, str(VAULT)])
        if proc.returncode != 0:
            return f"failed: {_err(proc)}"
        state = "done"
    copied = []
    for src in sorted(seed_dir.iterdir()):
        dest = VAULT / src.name
        if src.is_file() and not dest.exists():
            shutil.copy2(src, dest)
            copied.append(src.name)
    if copied:
        for cmd in (["git", "add", *copied],
                    ["git", "commit", "-m", "vault: add README and repo settings"],
                    ["git", "push"]):
            proc = _run(cmd, cwd=VAULT)
            if proc.returncode != 0:
                return f"failed: {' '.join(cmd[:2])}: {_err(proc)}"
        state = "done"
    else:
        ahead = _run(["git", "rev-list", "--count", "@{u}..HEAD"], cwd=VAULT)
        if ahead.returncode == 0 and ahead.stdout.strip().isdigit() and int(ahead.stdout) > 0:
            proc = _run(["git", "push"], cwd=VAULT)
            if proc.returncode != 0:
                return f"failed: git push: {_err(proc)}"
            state = "done"
    return state


def _step_project() -> str:
    bm = _bm()
    listing = _run([bm, "project", "list"])
    already = (listing.returncode == 0 and "vault" in listing.stdout
               and VAULT.name in listing.stdout.replace("\n", ""))
    cmds = []
    if not already:
        cmds.append([bm, "project", "add", "vault", str(VAULT)])
    cmds += [[bm, "project", "default", "vault"],
             [bm, "config", "set", "semantic_search_enabled", "true"],
             [bm, "config", "set", "semantic_embedding_provider", "fastembed"],
             [bm, "reindex"]]
    for cmd in cmds:
        proc = _run(cmd)
        if proc.returncode != 0:
            return f"failed: {' '.join(cmd[1:3])}: {_err(proc)}"
    return "already done" if already else "done"


def _step_mcp() -> str:
    if _run(["claude", "mcp", "get", "basic-memory"]).returncode == 0:
        return "already done"
    exe = _bm()
    if not Path(exe).is_absolute():
        return "failed: basic-memory executable not found"
    proc = _run(["claude", "mcp", "add", "basic-memory", "-s", "user",
                 "-e", "PYTHONUTF8=1", "-e", "PYTHONIOENCODING=utf-8",
                 "--", str(Path(exe).resolve()), "mcp"])
    return "done" if proc.returncode == 0 else f"failed: {_err(proc)}"


def _read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8") if path.exists() else ""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _step_hook() -> str:
    path = Path.home() / ".claude" / "settings.json"
    try:
        raw = _read_text(path)
        current = json.loads(raw) if raw.strip() else {}
        merged = merge_settings(current, hook_command_for())
        if merged == current and path.exists():
            return "already done"
        _backup(path)
        out = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
        if "\r\n" in raw:
            out = out.replace("\n", "\r\n")
        _write_text(path, out)
    except (OSError, ValueError) as exc:
        return f"failed: {exc}"
    return "done"


def _step_skill() -> str:
    src = REPO / "skill" / "SKILL.md"
    dest = Path.home() / ".claude" / "skills" / "vault" / "SKILL.md"
    try:
        if dest.exists() and dest.read_bytes() == src.read_bytes():
            return "already done"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    except OSError as exc:
        return f"failed: {exc}"
    return "done"


def _step_claude_md() -> str:
    path = Path.home() / ".claude" / "CLAUDE.md"
    try:
        text = _read_text(path)
        crlf = "\r\n" in text
        merged = merge_claude_md(text.replace("\r\n", "\n"))
        if crlf:
            merged = merged.replace("\n", "\r\n")
        if merged == text:
            return "already done"
        _backup(path)
        _write_text(path, merged)
    except OSError as exc:
        return f"failed: {exc}"
    return "done"


# (name, function, indexes of steps it depends on)
STEPS = [
    ("basic-memory: uv tool install", _step_basic_memory, None),
    ("clone: data repo and seed files", _step_clone, None),
    ("project: basic-memory project, search settings, reindex", _step_project, (0, 1)),
    ("mcp: register basic-memory server", _step_mcp, (0,)),
    ("hook: PostToolUse entry in settings.json", _step_hook, None),
    ("skill: copy vault skill", _step_skill, None),
    ("CLAUDE.md: add Knowledge vault section", _step_claude_md, None),
]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="kv install")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan without running anything or writing files")
    args = parser.parse_args(argv)

    if args.dry_run:
        for n, (name, _fn, _deps) in enumerate(STEPS, 1):
            _report(n, name, "would do")
        print(f"hook command: {hook_command_for()}")
        print(f"vault: {VAULT}")
        print("Dry run: nothing was changed.")
        return 0

    failed: set[int] = set()
    for idx, (name, fn, deps) in enumerate(STEPS):
        blocked = [d for d in (deps or ()) if d in failed]
        if blocked:
            failed.add(idx)
            _report(idx + 1, name, f"failed: depends on step {blocked[0] + 1}, which failed")
            continue
        state = fn()
        if state.startswith("failed"):
            failed.add(idx)
        _report(idx + 1, name, state)

    if failed:
        print(f"{len(failed)} step(s) failed. Fix the cause and run the install again.")
    print("Next: restart Claude Code sessions to load the basic-memory server and the vault skill.")
    return 1 if failed else 0
