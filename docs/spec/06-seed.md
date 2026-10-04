# 6. Seeding with this project's findings

v1 holds this project's own knowledge, written through the real path (basic-memory tools plus the hook), as the first proof that the whole loop works.

## Content
From `docs/research/d1-survey.md`, `docs/spike.md` and `docs/decisions.md`: about 15-20 notes, for example
- research: "Markdown vault MCP servers compared" (the survey);
- decisions: adopt basic-memory; tool code public, notes private; hybrid search; phone sync via Obsidian Git;
- findings: Obsidian Git is unstable on iOS but works read-mostly; Working Copy can't push for free; MCP tool search defers tool definitions; basic-memory token costs;
- patterns: Windows path length breaks Python installs; uv minor-version link error; bm CLI needs a UTF-8 console; clone Obsidian Git into a subfolder on iOS;
- the `knowledge-vault` hub.

## Acceptance criteria
- **Given** the seeded vault, **then** the checker reports no errors.
- **Then** the `knowledge-vault` hub lists every seeded note, and there is at least one note of each type pattern, finding, decision and research.
- **Then** every seeded note has a `source` pointing at a file in this repo.
- **Given** a reworded question for each of three seeded patterns, **when** searched, **then** the pattern ranks first.
- **Given** five questions written without looking at search results, **when** searched with the content-type filter, **then** at least four have a fitting note in the top 3 (the skill scans the top 3-5 titles).
- **Then** the seeded notes are on GitHub, and the owner sees them on the phone after a pull (gate check).
