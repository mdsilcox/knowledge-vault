"""Project links and hub notes. Spec: docs/spec/02-sync-hook.md."""
from datetime import date
from pathlib import Path

from kv.notes import read_text, note_paths, parse_note, wikilinks

START = "<!-- kv:notes -->"
END = "<!-- /kv:notes -->"
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "project.md"


def _read(path: Path) -> str:
    return read_text(path)


def _write(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _project(note) -> str | None:
    value = note.frontmatter.get("project")
    return str(value) if value else None


def ensure_project_links(vault: Path) -> list[Path]:
    """Append `Project: [[slug]]` to notes that lack the link. Text edit only."""
    changed = []
    for path in note_paths(vault):
        note = parse_note(path)
        project = _project(note)
        if not project or note.frontmatter.get("type") == "project":
            continue
        if project.lower() in [t.lower() for t in wikilinks(note.body)]:
            continue
        text = _read(path)
        nl = "\r\n" if "\r\n" in text else "\n"
        _write(path, f"{text.rstrip()}{nl}{nl}Project: [[{project}]]{nl}")
        changed.append(path)
    return changed


def _replace_block(text: str, lines: list[str]) -> str:
    nl = "\r\n" if "\r\n" in text else "\n"
    inner = nl + "".join(line + nl for line in lines)
    if START in text and END in text.split(START, 1)[1]:
        head, rest = text.split(START, 1)
        _, tail = rest.split(END, 1)
        return head + START + inner + END + tail
    return text.rstrip() + nl + nl + START + inner + END + nl


def update_hubs(vault: Path) -> list[Path]:
    """Rewrite each hub's generated list, creating missing hubs. Returns files changed."""
    vault = Path(vault)
    notes = [parse_note(p) for p in note_paths(vault)]
    members: dict[str, list] = {}
    hubs: dict[str, Path] = {}
    for n in notes:
        project = _project(n)
        if n.frontmatter.get("type") == "project":
            hubs[n.path.stem.lower()] = n.path
        elif project and not any(c in project for c in "/\\"):
            members.setdefault(project, []).append(n)
    changed = []
    for project in members:
        if project.lower() not in hubs:
            path = vault / "projects" / f"{project}.md"
            text = read_text(TEMPLATE).replace("\r\n", "\n")  # git may check templates out as CRLF
            text = text.replace("{{project}}", project).replace("{{date}}", date.today().isoformat())
            path.parent.mkdir(parents=True, exist_ok=True)
            _write(path, text)
            hubs[project.lower()] = path
            changed.append(path)
    for key, path in hubs.items():
        mine = [n for p, ns in members.items() if p.lower() == key for n in ns]
        mine.sort(key=lambda n: (str(n.frontmatter.get("type")), n.title.lower()))
        lines = [f"- [[{n.title}]] ({n.frontmatter.get('type')})" for n in mine]
        text = _read(path)
        new = _replace_block(text, lines)
        if new != text:
            _write(path, new)
            if path not in changed:
                changed.append(path)
    return changed
