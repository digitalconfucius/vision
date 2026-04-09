"""Query helpers over the wiki index."""
from collections import defaultdict
from typing import Any, Optional

from . import db


def slug_exists(slug: str) -> bool:
    conn = db.get_connection()
    row = conn.execute("SELECT 1 FROM pages WHERE slug = ?", (slug,)).fetchone()
    return row is not None


def all_slugs() -> set[str]:
    conn = db.get_connection()
    return {r["slug"] for r in conn.execute("SELECT slug FROM pages").fetchall()}


def get_page(slug: str) -> Optional[dict[str, Any]]:
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM pages WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def all_pages() -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT id, slug, title, folder, mtime, word_count FROM pages ORDER BY slug"
    ).fetchall()
    return [dict(r) for r in rows]


def recent_pages(limit: int = 15) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT id, slug, title, folder, mtime, word_count FROM pages "
        "ORDER BY mtime DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def folder_tree() -> dict:
    """Nested dict: {folder: {subfolder: [pages], ...}, ...}.
    For simplicity we support one level of nesting (top folder + pages),
    but the sidebar renders any depth via recursive templating of the pages list.
    """
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT slug, title, folder FROM pages ORDER BY slug"
    ).fetchall()
    tree: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        folder = r["folder"] or "_root"
        tree[folder].append({"slug": r["slug"], "title": r["title"]})
    # Stable alphabetical order of folders
    return dict(sorted(tree.items()))


def backlinks(slug: str) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        """
        SELECT DISTINCT p.id, p.slug, p.title, p.folder
        FROM links l
        JOIN pages p ON p.id = l.src_id
        WHERE l.dst_slug = ?
        ORDER BY p.slug
        """,
        (slug,),
    ).fetchall()
    return [dict(r) for r in rows]


def outgoing_links(page_id: int) -> list[dict]:
    """Outgoing links for a page with resolution info."""
    conn = db.get_connection()
    rows = conn.execute(
        """
        SELECT l.dst_slug, l.anchor, p.title AS dst_title
        FROM links l
        LEFT JOIN pages p ON p.slug = l.dst_slug
        WHERE l.src_id = ?
        ORDER BY l.dst_slug
        """,
        (page_id,),
    ).fetchall()
    seen = set()
    out = []
    for r in rows:
        key = r["dst_slug"]
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "slug": r["dst_slug"],
            "title": r["dst_title"] or r["dst_slug"],
            "broken": r["dst_title"] is None,
        })
    return out


def page_tags(page_id: int) -> list[str]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT tag FROM tags WHERE page_id = ? ORDER BY tag", (page_id,)
    ).fetchall()
    return [r["tag"] for r in rows]


def all_tags() -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT tag, COUNT(*) AS n FROM tags GROUP BY tag ORDER BY n DESC, tag"
    ).fetchall()
    return [dict(r) for r in rows]


def pages_for_tag(tag: str) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        """
        SELECT p.slug, p.title, p.folder, p.mtime
        FROM tags t
        JOIN pages p ON p.id = t.page_id
        WHERE t.tag = ?
        ORDER BY p.mtime DESC
        """,
        (tag,),
    ).fetchall()
    return [dict(r) for r in rows]


def search(query: str, limit: int = 50) -> list[dict]:
    if not query.strip():
        return []
    # FTS5 MATCH query — escape double quotes and wrap each term
    terms = [t for t in query.strip().split() if t]
    if not terms:
        return []
    fts_query = " ".join(f'"{t.replace(chr(34), "")}"*' for t in terms)
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """
            SELECT p.slug, p.title, p.folder,
                   snippet(pages_fts, 1, '<mark>', '</mark>', '…', 20) AS snippet,
                   bm25(pages_fts) AS rank
            FROM pages_fts
            JOIN pages p ON p.id = pages_fts.rowid
            WHERE pages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, limit),
        ).fetchall()
    except Exception:
        # Fallback to LIKE if FTS query is malformed
        like = f"%{query}%"
        rows = conn.execute(
            """
            SELECT slug, title, folder, substr(body, 1, 200) AS snippet, 0 AS rank
            FROM pages
            WHERE title LIKE ? OR body LIKE ?
            ORDER BY mtime DESC
            LIMIT ?
            """,
            (like, like, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def stats() -> dict:
    conn = db.get_connection()
    pages_n = conn.execute("SELECT COUNT(*) AS n FROM pages").fetchone()["n"]
    tags_n = conn.execute("SELECT COUNT(DISTINCT tag) AS n FROM tags").fetchone()["n"]
    links_n = conn.execute("SELECT COUNT(*) AS n FROM links").fetchone()["n"]
    # Orphans: pages with no backlinks and no outgoing links
    orphans_n = conn.execute(
        """
        SELECT COUNT(*) AS n FROM pages p
        WHERE NOT EXISTS (SELECT 1 FROM links WHERE dst_slug = p.slug)
          AND NOT EXISTS (SELECT 1 FROM links WHERE src_id = p.id)
        """
    ).fetchone()["n"]
    # Broken links: dst_slug not matching any page
    broken_n = conn.execute(
        """
        SELECT COUNT(DISTINCT dst_slug) AS n FROM links
        WHERE dst_slug NOT IN (SELECT slug FROM pages)
        """
    ).fetchone()["n"]
    return {
        "pages": pages_n,
        "tags": tags_n,
        "links": links_n,
        "orphans": orphans_n,
        "broken": broken_n,
    }


def orphans() -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        """
        SELECT p.slug, p.title, p.folder FROM pages p
        WHERE NOT EXISTS (SELECT 1 FROM links WHERE dst_slug = p.slug)
          AND NOT EXISTS (SELECT 1 FROM links WHERE src_id = p.id)
        ORDER BY p.slug
        """
    ).fetchall()
    return [dict(r) for r in rows]


def broken_links() -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        """
        SELECT l.dst_slug, p.slug AS src_slug, p.title AS src_title
        FROM links l
        JOIN pages p ON p.id = l.src_id
        WHERE l.dst_slug NOT IN (SELECT slug FROM pages)
        ORDER BY l.dst_slug
        """
    ).fetchall()
    return [dict(r) for r in rows]


def graph_data() -> dict:
    """Return {nodes: [...], edges: [...]} for the graph view."""
    conn = db.get_connection()
    pages = conn.execute("SELECT id, slug, title, folder FROM pages").fetchall()
    # Backlink counts per slug
    backlink_counts: dict[str, int] = defaultdict(int)
    for r in conn.execute("SELECT dst_slug, COUNT(*) AS n FROM links GROUP BY dst_slug").fetchall():
        backlink_counts[r["dst_slug"]] = r["n"]
    nodes = [
        {
            "id": p["slug"],
            "label": p["title"],
            "folder": p["folder"] or "",
            "value": backlink_counts.get(p["slug"], 0) + 1,
        }
        for p in pages
    ]
    existing_slugs = {p["slug"] for p in pages}
    edges_rows = conn.execute(
        """
        SELECT DISTINCT p.slug AS src, l.dst_slug AS dst
        FROM links l JOIN pages p ON p.id = l.src_id
        """
    ).fetchall()
    edges = [
        {"from": r["src"], "to": r["dst"]}
        for r in edges_rows
        if r["dst"] in existing_slugs
    ]
    return {"nodes": nodes, "edges": edges}
