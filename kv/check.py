"""Vault invariants. Spec: docs/spec/01-checker.md."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Problem:
    code: str
    path: Path
    message: str
    severity: str  # "error" | "warning"


def check_vault(vault: Path) -> list[Problem]:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    raise NotImplementedError
