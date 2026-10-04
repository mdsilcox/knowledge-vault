"""Spec: docs/spec/01-checker.md (secret patterns)."""
import pytest

from kv.secrets import find_secrets

SECRETS = {
    "GitHub token": "ghp_" + "A1b2" * 9,
    "GitHub fine-grained token": "github_pat_" + "A1b2C3" * 10,
    "Anthropic key": "sk-ant-api03-" + "x" * 40,
    "OpenAI key": "sk-" + "Ab1" * 10,
    "AWS access key": "AKIA" + "ABCDEFGHIJKLMNOP",
    "Private key": "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----",
    "Slack token": "xoxb-1234567890-abcdefghij",
    "Password assignment": "password: hunter22",
    "API key assignment": "api_key = 'abc123def456'",
}


@pytest.mark.parametrize("name", sorted(SECRETS))
def test_each_pattern_is_found(name):
    found = find_secrets(f"Some text before.\n{SECRETS[name]}\nAnd after.")
    assert found, name


def test_github_token_is_named():
    assert "GitHub token" in find_secrets("ghp_" + "A1b2" * 9)


@pytest.mark.parametrize("text", [
    "Use a fine-grained token scoped to one repo.",
    "The password field is in the plugin settings.",
    "password:",
    "Set api_key in your environment, never in a note.",
    "Ask for the task-runner sk-skill list.",
])
def test_ordinary_prose_is_clean(text):
    assert find_secrets(text) == []
