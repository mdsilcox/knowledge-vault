"""PostToolUse hook: project links, hubs, check, commit, push. Spec: docs/spec/02-sync-hook.md."""
from dataclasses import dataclass, field
from pathlib import Path

MATCHER = r"mcp__basic-memory__(write_note|edit_note|move_note|delete_note)"


@dataclass
class SyncResult:
    committed: bool = False
    pushed: bool = False
    blocked: bool = False
    message: str = ""
    warnings: list[str] = field(default_factory=list)


def handle_hook(payload: dict, vault: Path) -> SyncResult:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    raise NotImplementedError
