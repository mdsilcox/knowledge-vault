"""Secret pattern scan. Spec: docs/spec/01-checker.md."""
import re

_PATTERNS = [
    ("GitHub token", r"\b(?:gh[po]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    ("Anthropic key", r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    ("OpenAI key", r"\bsk-(?!ant-)[A-Za-z0-9_-]{20,}"),
    ("AWS access key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("Private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("Slack token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("Password assignment", r"(?i)\b(?:password|passwd|pwd)[ \t]*[:=][ \t]*['\"]?[^\s'\"]"),
    ("API key assignment", r"(?i)\bapi[_-]?key[ \t]*[:=][ \t]*['\"]?[^\s'\"]"),
]
_COMPILED = [(name, re.compile(rx)) for name, rx in _PATTERNS]


def find_secrets(text: str) -> list[str]:
    """Names of the secret patterns found in the text, each once."""
    return [name for name, rx in _COMPILED if rx.search(text)]
