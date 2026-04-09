"""Jinja filters."""
import datetime as dt

from flask import Flask

from .config import FOLDER_META, DEFAULT_FOLDER_ACCENT


def _fmt_mtime(value) -> str:
    try:
        ts = float(value)
    except (TypeError, ValueError):
        return ""
    now = dt.datetime.now()
    when = dt.datetime.fromtimestamp(ts)
    delta = now - when
    secs = int(delta.total_seconds())
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    if secs < 86400 * 7:
        return f"{secs // 86400}d ago"
    return when.strftime("%Y-%m-%d")


def _folder_label(folder: str) -> str:
    if not folder:
        return "Root"
    meta = FOLDER_META.get(folder)
    if meta and meta.get("label"):
        return meta["label"]
    return folder.replace("-", " ").replace("_", " ").title()


def _folder_icon(folder: str) -> str:
    meta = FOLDER_META.get(folder)
    if meta and meta.get("icon"):
        return meta["icon"]
    return "▢"


def _folder_accent(folder: str) -> str:
    meta = FOLDER_META.get(folder)
    if meta and meta.get("accent"):
        return meta["accent"]
    return DEFAULT_FOLDER_ACCENT


def _breadcrumb(slug: str) -> list[dict]:
    parts = slug.split("/")
    crumbs = []
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            crumbs.append({"label": part.replace("-", " ").replace("_", " "), "slug": None})
        else:
            crumbs.append({"label": _folder_label(part), "slug": None, "folder": part})
    return crumbs


def register(app: Flask) -> None:
    app.jinja_env.filters["mtime"] = _fmt_mtime
    app.jinja_env.filters["folder_label"] = _folder_label
    app.jinja_env.filters["folder_icon"] = _folder_icon
    app.jinja_env.filters["folder_accent"] = _folder_accent
    app.jinja_env.filters["breadcrumb"] = _breadcrumb
