"""Parse vault notes. Contract: docs/spec/README.md."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Note:
    path: Path
    frontmatter: dict
    body: str
    title: str


def parse_note(path: Path) -> Note:
    raise NotImplementedError


def wikilinks(text: str) -> list[str]:
    raise NotImplementedError
