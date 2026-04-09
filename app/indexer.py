"""Filesystem scanner — walks wiki/ and keeps the SQLite index fresh."""
import json
import os
import re
from pathlib import Path
from typing import Iterable

import frontmatter

from . import db
from .config import WIKI_DIR

# [[Target]] or [[Target|label]] — the target may contain slashes, spaces, dashes.
WIKILINK_RE = re.compile(r"\[\[([^\[\]\|]+?)(?:\|([^\[\]]+))?\]\]")
# Standard markdown link to a .md file
MDLINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s#]+?\.md)(?:#[^)]*)?\)")
# Inline #tag (not in code fences — simple heuristic)
INLINE_TAG_RE = re.compile(r"(?:(?<=\s)|^)#([a-zA-Z][\w-]{1,40})")


def _slug_from_path(rel_path: Path) -> str:
    """wiki/infra/vps.md  ->  infra/vps"""
    return str(rel_path.with_suffix("")).replace(os.sep, "/")


def _folder_from_slug(slug: str) -> str:
    return slug.split("/", 1)[0] if "/" in slug else ""


def _normalize_target(target: str) -> str:
    """Turn a wikilink target into a slug. Accepts 'Page Name', 'folder/page', etc."""
    t = target.strip()
    # If it looks like a path with slashes, lowercase the segments
    if "/" in t:
        return "/".join(seg.strip().lower().replace(" ", "-") for seg in t.split("/"))
    return t.lower().replace(" ", "-")


def _extract_title(post: frontmatter.Post, fallback: str) -> str:
    fm_title = post.metadata.get("title")
    if fm_title:
        return str(fm_title)
    for line in post.content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _extract_links(body: str) -> list[tuple[str, str]]:
    """Return [(dst_slug, anchor_text), ...]"""
    out: list[tuple[str, str]] = []
    for m in WIKILINK_RE.finditer(body):
        target, label = m.group(1), m.group(2)
        slug = _normalize_target(target)
        out.append((slug, (label or target).strip()))
    for m in MDLINK_RE.finditer(body):
        label, href = m.group(1), m.group(2)
        slug = href[:-3] if href.endswith(".md") else href
        slug = slug.lstrip("./").lower()
        out.append((slug, label.strip()))
    return out


def _extract_tags(post: frontmatter.Post) -> set[str]:
    tags: set[str] = set()
    fm_tags = post.metadata.get("tags")
    if isinstance(fm_tags, list):
        tags.update(str(t).strip().lstrip("#").lower() for t in fm_tags if str(t).strip())
    elif isinstance(fm_tags, str):
        tags.update(t.strip().lstrip("#").lower() for t in re.split(r"[,\s]+", fm_tags) if t.strip())
    # Inline tags from body (skip code fences)
    in_fence = False
    for line in post.content.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in INLINE_TAG_RE.finditer(line):
            tags.add(m.group(1).lower())
    return tags


def _walk_wiki() -> Iterable[Path]:
    if not WIKI_DIR.exists():
        return
    for dirpath, dirnames, filenames in os.walk(WIKI_DIR):
        # skip hidden dirs and assets
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "assets"]
        for name in filenames:
            if name.endswith(".md") and not name.startswith("."):
                yield Path(dirpath) / name


def _max_mtime() -> float:
    """Max mtime across wiki dir + file count sentinel."""
    mx = 0.0
    count = 0
    for p in _walk_wiki():
        mx = max(mx, p.stat().st_mtime)
        count += 1
    # Encode count into the sentinel so deletions also trigger refresh
    return mx + count * 1e-9


def reindex_all(force: bool = False) -> int:
    """Rescan wiki/ and rebuild the index. Returns number of pages indexed."""
    conn = db.raw_connection()
    try:
        cur = conn.cursor()
        found_paths: set[str] = set()
        n = 0

        for file in _walk_wiki():
            rel = file.relative_to(WIKI_DIR)
            rel_str = str(rel).replace(os.sep, "/")
            slug = _slug_from_path(rel)
            folder = _folder_from_slug(slug)
            mtime = file.stat().st_mtime

            found_paths.add(rel_str)

            # Check if existing row is up to date (unless forced)
            existing = cur.execute(
                "SELECT id, mtime FROM pages WHERE path = ?", (rel_str,)
            ).fetchone()
            if existing and not force and abs(existing["mtime"] - mtime) < 1e-6:
                continue

            try:
                post = frontmatter.load(file)
            except Exception:
                # Malformed frontmatter — treat file as plain body
                post = frontmatter.Post(file.read_text(encoding="utf-8"))

            body = post.content
            title = _extract_title(post, rel.stem.replace("-", " ").replace("_", " ").title())
            word_count = len(re.findall(r"\w+", body))
            fm_json = json.dumps(post.metadata, default=str)

            if existing:
                page_id = existing["id"]
                cur.execute(
                    """
                    UPDATE pages SET slug=?, title=?, body=?, frontmatter=?,
                        folder=?, mtime=?, word_count=?
                    WHERE id=?
                    """,
                    (slug, title, body, fm_json, folder, mtime, word_count, page_id),
                )
                cur.execute("DELETE FROM links WHERE src_id=?", (page_id,))
                cur.execute("DELETE FROM tags  WHERE page_id=?", (page_id,))
            else:
                cur.execute(
                    """
                    INSERT INTO pages (path, slug, title, body, frontmatter,
                        folder, mtime, word_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (rel_str, slug, title, body, fm_json, folder, mtime, word_count),
                )
                page_id = cur.lastrowid

            # Links
            for dst_slug, anchor in _extract_links(body):
                cur.execute(
                    "INSERT OR IGNORE INTO links (src_id, dst_slug, anchor) VALUES (?, ?, ?)",
                    (page_id, dst_slug, anchor),
                )

            # Tags
            for tag in _extract_tags(post):
                cur.execute(
                    "INSERT OR IGNORE INTO tags (page_id, tag) VALUES (?, ?)",
                    (page_id, tag),
                )

            n += 1

        # Remove rows for files no longer on disk
        all_paths = {row["path"] for row in cur.execute("SELECT path FROM pages").fetchall()}
        to_delete = all_paths - found_paths
        for path in to_delete:
            cur.execute("DELETE FROM pages WHERE path=?", (path,))

        # Store sentinel
        cur.execute(
            "INSERT INTO meta(key, value) VALUES('max_mtime', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(_max_mtime()),),
        )
        conn.commit()
        return n
    finally:
        conn.close()


def ensure_fresh() -> None:
    """Fast path: if max_mtime on disk matches the stored sentinel, do nothing."""
    conn = db.get_connection()
    row = conn.execute("SELECT value FROM meta WHERE key='max_mtime'").fetchone()
    current = _max_mtime()
    if row and abs(float(row["value"]) - current) < 1e-9:
        return
    reindex_all()
