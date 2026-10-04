"""Parse vault notes. Contract: docs/spec/README.md."""
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

FOLDERS = {
    "pattern": "patterns",
    "finding": "findings",
    "decision": "decisions",
    "research": "research",
    "note": "notes",
    "project": "projects",
}
_WIKILINK = re.compile(r"\[\[([^\[\]|#]+)(?:[#|][^\[\]]*)?\]\]")


@dataclass
class Note:
    path: Path
    frontmatter: dict
    body: str
    title: str


def read_text(path: Path) -> str:
    """Read UTF-8 text keeping line endings as they are."""
    return Path(path).read_bytes().decode("utf-8")


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter, body). Frontmatter is {} when missing or not a mapping."""
    text = text.lstrip("﻿")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                data = yaml.safe_load("".join(lines[1:i]))
            except yaml.YAMLError:
                return {}, text
            if not isinstance(data, dict):
                return {}, text
            return data, "".join(lines[i + 1:])
    return {}, text


def parse_note(path: Path) -> Note:
    text = read_text(path)
    fm, body = split_frontmatter(text)
    title = fm.get("title")
    return Note(Path(path), fm, body, str(title) if title not in (None, "") else Path(path).stem)


def wikilinks(text: str) -> list[str]:
    return [m.strip() for m in _WIKILINK.findall(text)]


def note_paths(vault: Path) -> list[Path]:
    """Every note under the type folders, skipping paths with a part starting with . or _."""
    found = []
    for folder in sorted(set(FOLDERS.values())):
        root = Path(vault) / folder
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            if any(part[0] in "._" for part in p.relative_to(vault).parts):
                continue
            found.append(p)
    return found
