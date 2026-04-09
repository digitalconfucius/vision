# CLAUDE.md — wiki maintenance instructions for Claude Code

You are the **maintainer** of the personal knowledge wiki that lives in this repo. The user curates sources and asks questions; you do all the bookkeeping — reading, summarizing, cross-referencing, filing, and keeping the wiki internally consistent. The human reads the wiki through a Flask app; you edit it directly as markdown files.

## Three-layer model

1. **`raw/`** — immutable source documents the user drops in (articles, pasted notes, transcripts, screenshots, exported configs). Read these but never modify them. This is the source of truth.
2. **`wiki/`** — LLM-maintained markdown pages. You own this layer. Create, update, and cross-reference pages here.
3. **`CLAUDE.md`** (this file) — how you operate.

The Flask app (`run.py`) reads `wiki/` and renders it. It rebuilds its SQLite index automatically when files change. You never touch `wiki.db` — it's derived.

## Directory conventions

```
wiki/
  index.md            # master index — curated catalog of everything, grouped by folder
  log.md              # append-only chronological log
  projects/           # active GitHub projects, repos, codebases
  infra/              # VPS, Tailscale, Cloudflare, DNS, machine setup
  apis/               # API keys, endpoints, quirks, rate limits
  reference/          # shortcuts, gotchas, "things I always forget"
  people/             # (optional) contacts, collaborators
  ideas/              # (optional) raw ideas, drafts, explorations
```

Put new pages in the most specific existing folder. Create new folders only when a topic clearly doesn't fit anywhere — and when you do, add an entry to `index.md` and consider updating `app/config.py` FOLDER_META for a nice icon/accent color.

## File naming

- `kebab-case.md` for page names.
- Slug = path without `.md`. Example: `wiki/infra/vps.md` → slug `infra/vps`.
- Avoid spaces, uppercase, or special chars in filenames.
- Optional `_README.md` per folder for a folder overview.

## Frontmatter schema

Every page should have YAML frontmatter:

```yaml
---
title: Hetzner VPS
tags: [infra, vps, ssh, hetzner]
created: 2026-04-09
updated: 2026-04-09
aliases: []   # optional alternate slugs
---
```

- `title` is what the reader sees in the page header, sidebar, and graph.
- `tags` are lowercase, no `#`, kebab-case. Inline `#tag` in body text is also picked up.
- `updated` — bump whenever you edit substantively.

## Wikilinks

Always prefer `[[slug]]` syntax over plain prose references:

- `[[infra/tailscale]]` → renders as link, shows up in graph.
- `[[infra/tailscale|my tailnet]]` → custom label.
- Missing targets render in red as broken — that's a signal you should either create the page or fix the link.

Use plain markdown links only for external URLs. Never link to `.md` files with standard markdown syntax unless you have a reason — `[[slug]]` is shorter and more semantic.

## Operations

### Ingest (new source arrives)

When the user adds something to `raw/` and asks you to process it:

1. Read the source carefully. Pull out facts, claims, entities, and anything that would be hard to find again.
2. Briefly tell the user what you found and where it will land.
3. Update or create the relevant pages in `wiki/`. A single source can touch 5–15 pages.
4. Add or update `[[wikilinks]]` between affected pages.
5. Update `wiki/index.md` if new pages were created.
6. Append a log entry (see below).
7. Bump `updated:` in frontmatter for touched pages.

### Query (user asks a question)

1. Read `wiki/index.md` first to see what's available.
2. Drill into relevant pages, following wikilinks as needed.
3. Answer with inline `[[citations]]` pointing to the pages you used.
4. Offer to file the answer back into the wiki as a new page if it's substantive — a comparison, a synthesis, a new insight.

### Lint (periodic health check)

When asked to lint or "clean up" the wiki:

- Find orphan pages (nothing links in or out). Suggest links or note they might belong under a different folder.
- Flag broken `[[wikilinks]]` — pages referenced but not created.
- Spot contradictions between pages and surface them.
- Suggest missing pages (concepts mentioned repeatedly in prose but without their own file).
- Note stale claims — sections older than a few months that newer sources may have superseded.

## Log format

`wiki/log.md` is append-only. Each entry is a level-2 heading with a consistent prefix so it's greppable:

```
## [2026-04-09] ingest | Hetzner Cloud docs
Added [[infra/hetzner]]; updated [[infra/vps]] with pricing tier table.

## [2026-04-09] query | "which machines are on tailnet?"
Answered from [[infra/tailscale]]; no updates needed.

## [2026-04-09] lint | weekly pass
3 broken links flagged, 2 orphans merged into [[reference/things-i-forget]].
```

Grep pattern for recent entries: `grep "^## \[" wiki/log.md | tail -10`.

## Style for wiki pages

- Lead with a 1–2 sentence summary so the reader gets value without scrolling.
- Use tables aggressively for anything tabular (machines, services, ports, keys).
- Prefer short sections with `##` headings — the right sidebar TOC makes them easy to navigate.
- Inline code blocks for commands, paths, IPs, keys. Fenced blocks for anything multi-line.
- When you're uncertain about a fact, mark it explicitly: `> **unverified:** ...`
- When content contradicts an earlier claim, flag it: `> **contradicts [[other-page]]:** ...`
- Never fabricate specifics (IP addresses, API keys, versions). If the user hasn't told you, ask or leave a `TODO:`.

## Sensitive content

Per the README, this repo holds nothing private. **Do not write actual secrets** into the wiki — keep API keys, passwords, and tokens in a password manager or `.env` file outside the repo. For API pages, document only: endpoint URLs, quirks, rate limits, doc links, and the *name* of the secret (e.g. `CLOUDFLARE_API_TOKEN`), never the value.

## Bootstrap

The wiki ships with seed pages under each folder. They have structure but no real content — fill them in by talking to the user and reading anything they drop in `raw/`. Start by asking the user what they want to focus on first and which existing pages are stubs worth fleshing out.
