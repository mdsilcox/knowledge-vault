# 1. Vault checker

Enforces the data model's invariants. Used by the sync hook on every write, by the tests, and by the owner (`python -m kv check <vault>`).

## Rules
| Code | Severity | Rule |
|---|---|---|
| `frontmatter-missing` | error | A note has no YAML frontmatter, or it doesn't parse. |
| `field-missing` | error | A required field is missing: `title`, `type`, `project`, `tags`, `created`, `status`. |
| `type-unknown` | error | `type` is not one of pattern, finding, decision, research, note, project. |
| `type-folder` | error | The note's folder doesn't match its type (e.g. a `finding` under `patterns/`). |
| `status-unknown` | error | `status` is not active or superseded. |
| `superseded-target` | error | A superseded note has no `superseded_by`, or it doesn't resolve. |
| `date-format` | error | `created` or `updated` is not `YYYY-MM-DD`. |
| `title-filename` | warning | `title` differs from the filename (without `.md`). |
| `title-duplicate` | error | Two notes share a title (case-insensitive). |
| `link-broken` | warning | A `[[wikilink]]` points at no note. |
| `hub-link-missing` | error | A non-hub note doesn't link to `[[<project>]]`. (The hook adds it, so this only fires for hand edits.) |
| `hub-missing` | error | A note's project has no hub in `projects/`. (The hook creates it.) |
| `secret` | error | Text matches a secret pattern. |

Files outside the type folders (README.md, anything starting with `.` or `_`) are ignored. Notes with `project: general` link to the `[[general]]` hub like any other project. A missing hub is reported once per note as `hub-missing`, not also as `link-broken`; an unknown `type` is reported as `type-unknown` only, not also as `type-folder`.

## Secret patterns
GitHub tokens (`ghp_`, `gho_`, `github_pat_`), Anthropic and OpenAI keys (`sk-ant-`, `sk-` followed by 20+ characters), AWS access keys (`AKIA` + 16), private key blocks (`-----BEGIN ... PRIVATE KEY-----`), Slack tokens (`xox[baprs]-`), and `password:` / `api_key =` style assignments with a non-empty value.

## Acceptance criteria
- **Given** a vault where every note follows the data model, **when** checked, **then** there are no problems.
- **Given** a vault with exactly one violation of a rule, **when** checked, **then** exactly one problem with that rule's code and the offending path is reported (one test per rule).
- **Given** `[[Title|alias]]` or `[[Title#Heading]]` pointing at an existing note, **then** no `link-broken`.
- **Given** a README.md at the vault root or files under `.obsidian/`, **then** they are not checked.
- **Given** text containing each secret pattern, **then** `find_secrets` names it; **given** ordinary prose about tokens ("use a fine-grained token"), **then** it finds nothing.
- `python -m kv check <vault>` exits 0 when there are no errors (warnings allowed) and 1 when there is any error, printing one line per problem.
