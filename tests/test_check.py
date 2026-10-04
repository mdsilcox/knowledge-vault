"""Spec: docs/spec/01-checker.md."""
import subprocess
import sys
from pathlib import Path

import pytest

from kv.check import check_vault
from tests.conftest import write_note


def codes(vault: Path) -> list[str]:
    return [p.code for p in check_vault(vault)]


def test_good_vault_has_no_problems(good_vault):
    assert check_vault(good_vault) == []


VIOLATIONS = {
    "field-missing": lambda v: write_note(v, "No status", status=None),
    "type-unknown": lambda v: write_note(v, "Odd type", type_="memo", folder="notes"),
    "type-folder": lambda v: write_note(v, "Misfiled", type_="finding", folder="patterns"),
    "status-unknown": lambda v: write_note(v, "Odd status", status="draft"),
    "superseded-target": lambda v: write_note(v, "Old news", status="superseded"),
    "date-format": lambda v: write_note(v, "Bad date", created="10/04/2026"),
    "title-filename": lambda v: write_note(v, "Name A", folder=None).rename(v / "findings" / "Name B.md"),
    "link-broken": lambda v: write_note(v, "Dangling", body="See [[Nowhere at all]]."),
    "hub-link-missing": lambda v: write_note(v, "Lonely", link_hub=False),
    "hub-missing": lambda v: write_note(v, "Orphan", project="unknown-project"),
    "secret": lambda v: write_note(v, "Leaky", body="token ghp_" + "a" * 36),
}


@pytest.mark.parametrize("code", sorted(VIOLATIONS))
def test_each_rule_reports_exactly_one_problem(good_vault, code):
    VIOLATIONS[code](good_vault)
    problems = check_vault(good_vault)
    assert [p.code for p in problems] == [code], problems
    assert problems[0].path.suffix == ".md"


def test_frontmatter_missing(good_vault):
    (good_vault / "findings" / "Bare.md").write_text("# Bare\nNo frontmatter.\n", encoding="utf-8")
    assert codes(good_vault) == ["frontmatter-missing"]


def test_title_duplicate_is_case_insensitive(good_vault):
    write_note(good_vault, "alpha FINDING", type_="note")
    assert "title-duplicate" in codes(good_vault)


def test_superseded_with_resolving_target_is_fine(good_vault):
    write_note(good_vault, "Old news", status="superseded", superseded_by="[[Alpha finding]]")
    assert check_vault(good_vault) == []


def test_severities(good_vault):
    write_note(good_vault, "Dangling", body="See [[Nowhere]].")
    write_note(good_vault, "Odd status", status="draft")
    sev = {p.code: p.severity for p in check_vault(good_vault)}
    assert sev == {"link-broken": "warning", "status-unknown": "error"}


def run_cli(vault: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "kv", "check", str(vault)], capture_output=True, text=True)


def test_cli_exit_codes(good_vault):
    assert run_cli(good_vault).returncode == 0
    write_note(good_vault, "Dangling", body="See [[Nowhere]].")
    assert run_cli(good_vault).returncode == 0  # warnings only
    write_note(good_vault, "Odd status", status="draft")
    result = run_cli(good_vault)
    assert result.returncode == 1
    assert len([line for line in result.stdout.splitlines() if line.strip()]) == 2
