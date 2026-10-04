"""Vault invariants. Spec: docs/spec/01-checker.md."""
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from kv.notes import read_text, FOLDERS, note_paths, parse_note, wikilinks
from kv.secrets import find_secrets

REQUIRED = ["title", "type", "project", "tags", "created", "status"]
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Problem:
    code: str
    path: Path
    message: str
    severity: str  # "error" | "warning"


def _valid_date(value) -> bool:
    if isinstance(value, datetime):
        return False
    if isinstance(value, date):
        return True
    if isinstance(value, str) and _DATE.match(value):
        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False
    return False


def _flatten(value) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [s for v in value for s in _flatten(v)]
    return [] if value is None else [str(value)]


def _link_targets(value) -> list[str]:
    out = []
    for s in _flatten(value):
        out.extend(wikilinks(s) or [s])
    return out


def check_vault(vault: Path) -> list[Problem]:
    vault = Path(vault)
    problems: list[Problem] = []

    def add(code, path, message, severity="error"):
        problems.append(Problem(code, path, message, severity))

    notes = []
    for path in note_paths(vault):
        text = read_text(path)
        notes.append((parse_note(path), text))
    names = set()
    for note, _ in notes:
        names.add(note.title.lower())
        names.add(note.path.stem.lower())
    titles: dict[str, list] = {}
    hubs = {n.path.stem.lower() for n, _ in notes if n.frontmatter.get("type") == "project"}

    for note, text in notes:
        path, fm = note.path, note.frontmatter
        for name in find_secrets(text):
            add("secret", path, f"Possible secret: {name}")
        if not fm:
            add("frontmatter-missing", path, "No readable YAML frontmatter")
            continue
        titles.setdefault(note.title.lower(), []).append(path)
        for field in REQUIRED:
            if fm.get(field) is None:
                add("field-missing", path, f"Missing field: {field}")
        type_ = fm.get("type")
        if type_ is not None:
            if type_ not in FOLDERS:
                add("type-unknown", path, f"Unknown type: {type_}")
            elif path.relative_to(vault).parts[0] != FOLDERS[type_]:
                add("type-folder", path, f"A {type_} belongs in {FOLDERS[type_]}/")
        status = fm.get("status")
        if status is not None and status not in ("active", "superseded"):
            add("status-unknown", path, f"Unknown status: {status}")
        if status == "superseded":
            targets = _link_targets(fm.get("superseded_by"))
            if not targets or not all(t.lower() in names for t in targets):
                add("superseded-target", path, "Superseded note needs a superseded_by that resolves")
        for field in ("created", "updated"):
            if fm.get(field) is not None and not _valid_date(fm[field]):
                add("date-format", path, f"{field} must be YYYY-MM-DD")
        if fm.get("title") is not None and str(fm["title"]) != path.stem:
            add("title-filename", path, "Title differs from the filename", "warning")
        project = fm.get("project")
        project = str(project) if project is not None else None
        is_hub = type_ == "project"
        hub_missing = bool(project) and not is_hub and project.lower() not in hubs
        links = wikilinks(note.body)
        if hub_missing:
            add("hub-missing", path, f"No hub note projects/{project}.md")
        elif project and not is_hub and project.lower() not in [t.lower() for t in links]:
            add("hub-link-missing", path, f"Missing link to [[{project}]]")
        for target in dict.fromkeys(links):
            if target.lower() in names:
                continue
            if hub_missing and project and target.lower() == project.lower():
                continue
            add("link-broken", path, f"Broken link [[{target}]]", "warning")

    for same in titles.values():
        if len(same) > 1:
            for path in same:
                add("title-duplicate", path, "Another note has the same title")
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python -m kv check <vault>", file=sys.stderr)
        return 2
    vault = Path(argv[0])
    problems = check_vault(vault)
    for p in problems:
        try:
            shown = p.path.relative_to(vault)
        except ValueError:
            shown = p.path
        print(f"{p.severity} {p.code} {shown.as_posix()}: {p.message}")
    return 1 if any(p.severity == "error" for p in problems) else 0
