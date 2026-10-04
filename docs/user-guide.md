# Knowledge vault: user guide

For the owner. Short steps, one command per block. Commands run in PowerShell unless noted.

## 1. What the vault is

The vault is a folder of plain Markdown notes that holds the reusable findings of all your projects: lessons learned, research, decisions and patterns. Claude Code searches it only when needed and writes to it at set moments (see section 4). You read it in Obsidian on the PC and the iPhone. Only key, reusable findings go in; each project keeps its own memory and docs. Full details: [vision](vision.md).

- Vault folder on the PC: `E:\Backup Desktop\Claude Code Projects\knowledge-vault-data`
- Private GitHub repo for the notes: `mdsilcox/knowledge-vault-data`
- Public repo for the tool code (this repo): `mdsilcox/knowledge-vault`

## 2. Install on a new PC

You need: [uv](https://docs.astral.sh/uv/), git with access to your GitHub account, and Claude Code.

1. Clone this repo.

   ```
   git clone https://github.com/mdsilcox/knowledge-vault
   ```

2. Go into the folder and set up its Python environment.

   ```
   cd knowledge-vault
   ```

   ```
   uv sync
   ```

3. Preview what the install will do. Nothing is changed.

   ```
   uv run python -m kv install --dry-run
   ```

4. Run the real install.

   ```
   uv run python -m kv install
   ```

5. Restart Claude Code so it loads the basic-memory server and the vault skill.

The installer can be run again safely: a step that is already done says "already done". If a step fails, fix the cause and run it again.

The vault path is fixed in `kv/install.py` (`VAULT`). If the vault should live somewhere else on the new PC, change that line before step 4.

### What the install changes

1. Installs basic-memory (`uv tool install basic-memory`), the search server.
2. Clones the private data repo into the vault folder and adds its README and repo settings.
3. Adds a basic-memory project named `vault`, makes it the default, turns on local search by meaning, and builds the search index.
4. Registers the basic-memory server with Claude Code for all projects (`claude mcp add basic-memory -s user`).
5. Adds a `PostToolUse` hook to `~/.claude/settings.json`. After every vault write it checks the note, updates the project hub, commits and pushes.
6. Copies the vault skill to `~/.claude/skills/vault/SKILL.md`.
7. Adds a "## Knowledge vault" section to `~/.claude/CLAUDE.md`.

`~/.claude/settings.json` and `~/.claude/CLAUDE.md` are backed up first as `settings.json.bak-YYYYMMDD` and `CLAUDE.md.bak-YYYYMMDD` (same folder). Your other settings and text are kept.

### Undo

The vault folder and its GitHub repo are never touched by an undo.

1. Remove the server from Claude Code.

   ```
   claude mcp remove basic-memory -s user
   ```

2. In `~/.claude/settings.json`, restore the `.bak-YYYYMMDD` copy, or delete the `PostToolUse` entry whose `matcher` starts with `mcp__basic-memory__`.
3. Delete the folder `~/.claude/skills/vault/`.
4. In `~/.claude/CLAUDE.md`, delete the "## Knowledge vault" section.
5. Remove the basic-memory project.

   ```
   basic-memory project remove vault
   ```

6. Uninstall basic-memory.

   ```
   uv tool uninstall basic-memory
   ```

## 3. Phone setup (iPhone, read only)

You use the free Obsidian app and its free Git plugin. You need a fine-grained GitHub token limited to the `knowledge-vault-data` repo with "Contents: read and write". Create it in GitHub under Settings, Developer settings, Personal access tokens.

1. In Obsidian, create a new vault. **Do not store it in iCloud.**
2. Settings, Community plugins: turn them on, then install and enable **Git**.
3. Do not open the Git plugin's authentication settings before cloning. With no repo yet it shows `fatal: --local can only be used inside a git repository`. This is harmless, but avoid it.
4. Open the command palette and run **Git: Clone an existing remote repo**.
5. Enter the URL, then your username, then the token as the password.

   ```
   https://github.com/mdsilcox/knowledge-vault-data.git
   ```

   Username: `mdsilcox`. Password: the token.
6. **Clone into a subfolder** such as `vault`, not the vault root. The root already holds Obsidian's `.obsidian` folder, so a root clone fails with `destination already exists and is not an empty directory`. A subfolder also keeps the phone's Obsidian settings out of the repo. Afterward check Settings, Git, Advanced: "Custom base path" should say `vault`.
7. Leave the Identity (commit author) section empty. The phone only reads.

The two traps, in short: do not clone into the vault root, and do not open the auth settings before cloning.

To get new notes later, open the command palette and run **Git: Pull**. The phone is read only: write notes from the PC, through Claude. Search by meaning works only on the PC; the phone has Obsidian's keyword search.

## 4. Everyday use

You mostly talk to Claude in any project; it loads the vault tools only when needed. Claude uses four tools: search, read, write and edit.

| You say | What Claude does |
|---|---|
| "Save this to the vault" | Searches first. If a note already covers it, adds to that note. Otherwise writes a new note of the right type (pattern, finding, decision, research or note) with a short title, tags and a link back to the project. |
| "Have we solved this before?" or "Have we seen this before?" | Searches by meaning, reads the best one or two notes, uses them, and says which note helped. |
| "What do we know about <project>?" | Reads that project's hub in `projects/`, which lists every note from the project. |
| "Check the vault before we pick a library" | Searches the vault for earlier research and decisions on the topic before it starts researching. |

Claude also writes without being asked at these moments: after a research report, when a reusable decision is logged, at a phase retro, and when a problem is solved in a way worth reusing. It does not write one-project trivia, whole transcripts, copies of project docs, or secrets.

After every write, the hook adds the project link, updates the hub, commits and pushes. You do not need to do any of that.

Claude asks you first before it:

- deletes, moves, renames or supersedes a note (a superseded note stays, marked `status: superseded` and pointing to the newer one);
- writes anything that might be sensitive or personal;
- rewrites most of an existing note.

## 5. Browsing in Obsidian

On the PC, open the vault folder `E:\Backup Desktop\Claude Code Projects\knowledge-vault-data` as an Obsidian vault. On the phone, see section 3.

- **Folders by type:** `patterns/`, `findings/`, `decisions/`, `research/`, `notes/`.
- **Project hubs:** `projects/` holds one hub per project, listing all its notes. Start there to see everything from one project.
- **Links:** click a `[[link]]` to jump to a related note.
- **Graph view:** shows how notes and projects connect. Open it from the left ribbon or the command palette.
- **Search:** Obsidian's search finds words in titles and text.
- **Phone updates:** run **Git: Pull** from the command palette.

Notes are ordinary text files, so any editor opens them. If you edit a note yourself on the PC, the hook commits and pushes your change together with Claude's next vault write, or you can push it yourself (see "A push failed" in section 6).

## 6. Fixing things

**Before any `basic-memory` command,** set these two variables in the same PowerShell window, or the command crashes with `UnicodeEncodeError` while drawing its spinner. (The installer already sets both for the Claude Code server.)

```
$env:PYTHONUTF8 = "1"
```

```
$env:PYTHONIOENCODING = "utf-8"
```

**Rebuild the search index.** The index is only a cache; the notes are the source of truth. Nothing is lost.

```
basic-memory reindex --full
```

**A push failed.** The hook says "The note is saved locally and will be pushed with the next write." Either do another write, or push by hand.

```
git -C "E:\Backup Desktop\Claude Code Projects\knowledge-vault-data" push
```

**A write was blocked for a possible secret.** The hook says "Nothing was committed: possible secrets found" and names the note. Remove the secret from the note, then ask Claude to write again.

**Check the vault for problems** (broken links, bad frontmatter, secrets). Run it in this repo's folder.

```
uv run python -m kv check "E:\Backup Desktop\Claude Code Projects\knowledge-vault-data"
```

No output means no problems.

**Update basic-memory.** Upgrade it, then run the real-basic-memory tests in this repo to confirm that nothing broke.

```
uv tool upgrade basic-memory
```

```
uv run pytest -m slow
```

## 7. Later: seeding other projects

The vault starts with this project's findings. To add another project, open Claude Code in that project and ask it to file its key findings in the vault at its next retro. Claude writes the notes, tags them with the project, and the hub appears in `projects/`. Candidates: Blue Dragon Tuner, Russian Trainer, Orchestration Lab.
