"""Project links and hub notes. Spec: docs/spec/02-sync-hook.md."""
from pathlib import Path

START = "<!-- kv:notes -->"
END = "<!-- /kv:notes -->"


def ensure_project_links(vault: Path) -> list[Path]:
    raise NotImplementedError


def update_hubs(vault: Path) -> list[Path]:
    raise NotImplementedError
