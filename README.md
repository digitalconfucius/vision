# vision

A personal LLM wiki. Global knowledge base for dev and business — projects, infra, APIs, configs, shortcuts, random things I forget. Nothing private.

Markdown files on disk, a Flask reader on top, and Claude Code as the maintainer.

## The idea

Three layers:

1. **`raw/`** — source material I drop in (articles, notes, transcripts, exported configs). Immutable.
2. **`wiki/`** — interlinked markdown pages. Claude Code owns this layer — reads sources, extracts info, creates and updates pages, maintains cross-references.
3. **[CLAUDE.md](CLAUDE.md)** — instructions that turn Claude Code into a disciplined wiki maintainer.

The Flask app is just the reader: fast navigation, full-text search, backlinks, tags, graph view. I never write the wiki by hand — I talk to Claude Code, and it edits the files.

## Stack

- Python 3.10+
- Flask
- SQLite3 with FTS5 (as a derived index, not the source of truth)
- `markdown` + `python-frontmatter` + Pygments
- vis-network (CDN) for the graph view

No build step, no node_modules, no external services.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open <http://127.0.0.1:5050>.

## Layout

```
vision/
├── CLAUDE.md          # schema — how Claude Code maintains the wiki
├── run.py             # Flask entrypoint
├── requirements.txt
├── app/               # Flask app (reader/navigator)
│   ├── indexer.py     # walks wiki/, keeps SQLite index fresh
│   ├── markdown_ext.py# [[wikilink]] + [](page.md) rewriting
│   ├── models.py      # queries: search, backlinks, graph, orphans
│   ├── routes.py      # dashboard, page, edit, search, graph, tags, log
│   ├── templates/     # Jinja templates
│   └── static/        # css + js
├── wiki/              # the knowledge base (markdown)
│   ├── index.md
│   ├── log.md
│   ├── projects/
│   ├── infra/         # vps, tailscale, cloudflare, new-machine-setup
│   ├── apis/
│   └── reference/     # shortcuts, things-i-forget
├── raw/               # (gitignored) drop sources here
└── wiki.db            # (gitignored) derived search index
```

## Features

- **Dense Obsidian-style UI** — three-column layout, collapsible sidebars, folder tree, tags, recent pages
- **Full-text search** — FTS5 with `<mark>`-highlighted snippets; `/` to focus, arrow keys + enter
- **Wikilinks** — `[[slug]]` auto-links; broken targets rendered in red
- **Backlinks** — every page lists who links to it
- **Graph view** — force-directed, colored by folder, sized by backlink count
- **Orphan + broken-link detection** — surfaced on the dashboard
- **Keyboard-first** — `/` `g h` `g g` `g i` `g t` `g l` `e` `n` `[` `]` `?`
- **Auto-reindex** — any file change is picked up on the next request
- **Manual edits** — quick textarea for fixes; Claude Code is the primary author

## Workflow

1. Drop a source in `raw/` (or paste content in a chat).
2. Tell Claude Code in this repo: *"read `raw/xyz` and update the wiki per CLAUDE.md"*.
3. Claude reads [CLAUDE.md](CLAUDE.md), edits the relevant pages in `wiki/`, adds wikilinks, updates `wiki/index.md`, and appends to `wiki/log.md`.
4. Refresh the browser. Everything reindexes automatically.

## Non-goals

- No LLM API integration inside the Flask app. Claude Code is the maintainer, running on the repo directly.
- No auth. Binds to `127.0.0.1` only.
- No WYSIWYG editor. Plain textarea for quick fixes.
- No secrets in the repo. API pages document *names* (`CLOUDFLARE_API_TOKEN`), not values.
