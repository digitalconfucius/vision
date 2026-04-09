"""SQLite connection and schema."""
import sqlite3
from typing import Optional

from flask import g

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    id          INTEGER PRIMARY KEY,
    path        TEXT UNIQUE NOT NULL,
    slug        TEXT UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    frontmatter TEXT,
    folder      TEXT NOT NULL,
    mtime       REAL NOT NULL,
    word_count  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pages_folder ON pages(folder);
CREATE INDEX IF NOT EXISTS idx_pages_mtime  ON pages(mtime DESC);

CREATE TABLE IF NOT EXISTS links (
    src_id    INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    dst_slug  TEXT NOT NULL,
    anchor    TEXT,
    PRIMARY KEY (src_id, dst_slug, anchor)
);
CREATE INDEX IF NOT EXISTS idx_links_dst ON links(dst_slug);

CREATE TABLE IF NOT EXISTS tags (
    page_id INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    tag     TEXT NOT NULL,
    PRIMARY KEY (page_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
    title, body, slug,
    content='pages', content_rowid='id',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
    INSERT INTO pages_fts(rowid, title, body, slug)
    VALUES (new.id, new.title, new.body, new.slug);
END;

CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
    INSERT INTO pages_fts(pages_fts, rowid, title, body, slug)
    VALUES ('delete', old.id, old.title, old.body, old.slug);
END;

CREATE TRIGGER IF NOT EXISTS pages_au AFTER UPDATE ON pages BEGIN
    INSERT INTO pages_fts(pages_fts, rowid, title, body, slug)
    VALUES ('delete', old.id, old.title, old.body, old.slug);
    INSERT INTO pages_fts(rowid, title, body, slug)
    VALUES (new.id, new.title, new.body, new.slug);
END;
"""


def get_connection() -> sqlite3.Connection:
    """Per-request connection (stored on flask.g)."""
    conn: Optional[sqlite3.Connection] = getattr(g, "_db_conn", None)
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g._db_conn = conn
    return conn


def close_connection(exc=None) -> None:
    conn = getattr(g, "_db_conn", None)
    if conn is not None:
        conn.close()
        g._db_conn = None


def raw_connection() -> sqlite3.Connection:
    """Standalone connection not tied to flask.g (used during startup/indexing)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create schema if not present."""
    conn = raw_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
