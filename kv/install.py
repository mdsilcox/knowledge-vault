"""PC setup: basic-memory, MCP registration, hook, skill, CLAUDE.md. Spec: docs/spec/03-install.md."""

CLAUDE_MD_HEADING = "## Knowledge vault"


def merge_settings(settings: dict, hook_command: str) -> dict:
    raise NotImplementedError


def merge_claude_md(text: str) -> str:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    raise NotImplementedError
