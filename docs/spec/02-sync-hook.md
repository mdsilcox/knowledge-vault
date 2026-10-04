# 2. Sync hook

A Claude Code `PostToolUse` hook that runs after every vault write, so the owner's phone sees each note without anyone remembering to push.

## Trigger
Registered in `~/.claude/settings.json` with matcher `mcp__basic-memory__(write_note|edit_note|move_note|delete_note)`; command `"<repo>/.venv/Scripts/python.exe" -m kv sync --vault "<vault path>"`. Any other tool is ignored (exit 0, no git activity).

## What it does, in order
1. **Project links:** every non-hub note whose body lacks `[[<project>]]` gets a final line `Project: [[<project>]]`.
2. **Hubs:** for every project slug in use, `projects/<slug>.md` exists (created from the project template when missing), and the block between `<!-- kv:notes -->` and `<!-- /kv:notes -->` lists that project's notes as `- [[Title]] (type)`, sorted by type then title. Text outside the markers is never touched.
3. **Check:** runs the checker on the whole vault.
4. **Secrets block:** if any `secret` problem exists in a file changed by this write (from `git status`), nothing is committed; exit 2 with a message naming the file and pattern and asking Claude to remove it. Only changed files count, so a secret already in history can't block every later write; the file stays blocked until it is fixed, because it stays changed.
5. **Commit:** `git add -A`, one commit, message `vault: <created|updated|moved|deleted> <title>` (from the tool name and `tool_input.title`, or the identifier when there is no title). No commit when nothing changed.
6. **Push:** `git push`. If rejected, `git pull --rebase` and push once more. If it still fails, or there is no network, the commit stays local; exit 2 telling Claude the note is saved but not yet on GitHub (the next write pushes it).
7. **Warnings:** any other check problems are reported to Claude via exit 2 after the push, so it can fix them; the write itself has already happened.

Clean run: exit 0, nothing shown in the transcript.

## Acceptance criteria
- **Given** a hook payload for `write_note` with a new note, **when** the hook runs, **then** there is one new commit `vault: created <title>` on the remote, containing the note, its project link and the updated hub.
- **Given** an `edit_note` payload, **then** the commit message says `updated`.
- **Given** a payload for a non-vault tool (e.g. `mcp__github__search`), **then** no commit and exit 0.
- **Given** no changes in the vault, **then** no empty commit.
- **Given** a note containing a GitHub token, **then** nothing is committed, the remote is unchanged, `blocked` is true, and the message names the file and "GitHub token".
- **Given** the remote has a commit the local clone lacks (no conflict), **then** the hook rebases and pushes; the remote has both commits.
- **Given** the remote is unreachable, **then** the commit exists locally, `pushed` is false, and the message says it will push next time; **given** the next write with the remote back, **then** both commits reach the remote.
- **Given** a hub with hand-written text outside the markers, **when** hubs update, **then** that text is unchanged and only the marked block changes.
- **Given** a note for a project with no hub, **then** `projects/<slug>.md` is created with the marked block.
- Running the hook twice on the same state makes no second commit (idempotent).
