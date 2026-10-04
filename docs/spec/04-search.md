# 4. Search through basic-memory

No code of ours: this spec pins the upstream behavior we rely on, so a basic-memory upgrade that breaks it fails a test.

## Acceptance criteria (slow tests, real basic-memory, throwaway config)
- **Given** the 15-note fixture vault from the spike (`tests/fixtures/spike_vault/`), **when** each of the 4 reworded questions from `docs/spike.md` is searched in the default mode, **then** the expected note ranks first.
- **Given** a note written with `write_note` through the CLI, **then** its file has frontmatter `title`, `type`, `tags`, `permalink` and the body verbatim.
- **Given** an indexed vault, **when** `memory.db` is deleted and the vault reindexed, **then** the same 4 questions give the same top results, and no note file changes.
- **Given** a note edited on disk outside basic-memory, **when** reindexed, **then** a search for the new text finds it.
