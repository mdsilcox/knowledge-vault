"""Spec: docs/spec/02-sync-hook.md (steps 1 and 2)."""
from kv.hubs import END, START, ensure_project_links, update_hubs
from kv.notes import parse_note
from tests.conftest import write_hub, write_note


def block(hub_text: str) -> list[str]:
    inner = hub_text.split(START, 1)[1].split(END, 1)[0]
    return [line for line in inner.splitlines() if line.strip()]


def test_project_link_is_added_when_missing(tmp_path):
    vault = tmp_path / "v"
    write_hub(vault)
    path = write_note(vault, "Lonely", link_hub=False)
    assert ensure_project_links(vault) == [path]
    assert parse_note(path).body.rstrip().endswith("Project: [[demo]]")
    assert ensure_project_links(vault) == []  # idempotent


def test_hub_lists_notes_sorted_by_type_then_title(tmp_path):
    vault = tmp_path / "v"
    hub = write_hub(vault)
    write_note(vault, "Zeta finding")
    write_note(vault, "Alpha finding")
    write_note(vault, "Middle pattern", type_="pattern")
    write_note(vault, "Other project note", project="elsewhere")
    write_hub(vault, "elsewhere")
    update_hubs(vault)
    assert block(hub.read_text(encoding="utf-8")) == [
        "- [[Alpha finding]] (finding)",
        "- [[Zeta finding]] (finding)",
        "- [[Middle pattern]] (pattern)",
    ]


def test_text_outside_markers_is_untouched(tmp_path):
    vault = tmp_path / "v"
    hub = write_hub(vault, extra="Hand-written intro the owner cares about.")
    write_note(vault, "Alpha finding")
    before = hub.read_text(encoding="utf-8")
    update_hubs(vault)
    after = hub.read_text(encoding="utf-8")
    assert before.split(START)[0] == after.split(START)[0]
    assert before.split(END)[1] == after.split(END)[1]
    assert block(after) == ["- [[Alpha finding]] (finding)"]


def test_missing_hub_is_created(tmp_path):
    vault = tmp_path / "v"
    write_note(vault, "First note", project="new-project")
    changed = update_hubs(vault)
    hub = vault / "projects" / "new-project.md"
    assert hub in changed
    note = parse_note(hub)
    assert note.frontmatter["type"] == "project"
    assert note.frontmatter["project"] == "new-project"
    assert block(hub.read_text(encoding="utf-8")) == ["- [[First note]] (finding)"]


def test_created_hub_has_lf_line_endings(tmp_path):
    vault = tmp_path / "v"
    write_note(vault, "First note", project="new-project")
    update_hubs(vault)
    assert b"\r\n" not in (vault / "projects" / "new-project.md").read_bytes()


def test_update_hubs_is_idempotent(tmp_path):
    vault = tmp_path / "v"
    write_hub(vault)
    write_note(vault, "Alpha finding")
    update_hubs(vault)
    assert update_hubs(vault) == []
