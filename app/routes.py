"""Flask routes."""
import re
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from . import indexer, markdown_ext, models
from .config import WIKI_DIR

bp = Blueprint("wiki", __name__)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9/_\-]*$")


def _common_ctx() -> dict:
    """Context available to every template via direct passing (sidebar data)."""
    return {
        "folder_tree": models.folder_tree(),
        "recent_pages": models.recent_pages(12),
        "all_tags": models.all_tags()[:20],
        "stats": models.stats(),
    }


def _render_body(body: str) -> tuple[str, list]:
    existing = models.all_slugs()
    return markdown_ext.render(body, exists_fn=lambda s: s in existing)


@bp.before_request
def _ensure_fresh_index():
    # Keep the index in sync on every request (cheap on unchanged fs).
    indexer.ensure_fresh()


@bp.route("/")
def dashboard():
    ctx = _common_ctx()
    ctx.update({
        "orphans": models.orphans()[:8],
        "broken_links": models.broken_links()[:8],
        "folders": list(ctx["folder_tree"].keys()),
    })
    return render_template("dashboard.html", **ctx)


@bp.route("/w/<path:slug>")
def view_page(slug: str):
    slug = slug.rstrip("/")
    page = models.get_page(slug)
    if not page:
        # Offer to create
        return render_template(
            "missing.html",
            slug=slug,
            **_common_ctx(),
        ), 404
    html, toc = _render_body(page["body"])
    ctx = _common_ctx()
    ctx.update({
        "page": page,
        "html": html,
        "toc": toc,
        "backlinks": models.backlinks(slug),
        "outgoing": models.outgoing_links(page["id"]),
        "tags": models.page_tags(page["id"]),
    })
    return render_template("page.html", **ctx)


@bp.route("/w/<path:slug>/edit", methods=["GET", "POST"])
def edit_page(slug: str):
    slug = slug.rstrip("/")
    page = models.get_page(slug)
    if not page:
        abort(404)
    file_path = WIKI_DIR / page["path"]

    if request.method == "POST":
        new_body = request.form.get("body", "")
        # Preserve frontmatter: if file starts with ---, keep that block when the new_body doesn't already have one
        new_text = new_body.replace("\r\n", "\n")
        if not new_text.endswith("\n"):
            new_text += "\n"
        file_path.write_text(new_text, encoding="utf-8")
        indexer.reindex_all(force=True)
        return redirect(url_for("wiki.view_page", slug=slug))

    raw_text = file_path.read_text(encoding="utf-8") if file_path.exists() else page["body"]
    ctx = _common_ctx()
    ctx.update({"page": page, "raw_text": raw_text})
    return render_template("edit.html", **ctx)


@bp.route("/new", methods=["GET", "POST"])
def new_page():
    if request.method == "POST":
        slug = (request.form.get("slug") or "").strip().lower().replace(" ", "-")
        title = (request.form.get("title") or "").strip()
        body = request.form.get("body") or ""
        if not slug or not SLUG_RE.match(slug):
            return render_template(
                "new.html",
                error="Slug must be lowercase, use letters/digits/-/_ and optional / for folders.",
                form={"slug": slug, "title": title, "body": body},
                **_common_ctx(),
            )
        rel_path = Path(slug + ".md")
        abs_path = WIKI_DIR / rel_path
        if abs_path.exists():
            return render_template(
                "new.html",
                error=f"Page already exists: {slug}",
                form={"slug": slug, "title": title, "body": body},
                **_common_ctx(),
            )
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        if not title:
            title = slug.split("/")[-1].replace("-", " ").replace("_", " ").title()
        content = f"---\ntitle: {title}\ntags: []\n---\n\n# {title}\n\n{body}\n"
        abs_path.write_text(content, encoding="utf-8")
        indexer.reindex_all(force=True)
        return redirect(url_for("wiki.view_page", slug=slug))

    prefill_slug = request.args.get("slug", "")
    return render_template(
        "new.html",
        error=None,
        form={"slug": prefill_slug, "title": "", "body": ""},
        **_common_ctx(),
    )


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = models.search(q) if q else []
    ctx = _common_ctx()
    ctx.update({"q": q, "results": results})
    return render_template("search.html", **ctx)


@bp.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    results = models.search(q, limit=10) if q else []
    return jsonify({"q": q, "results": results})


@bp.route("/graph")
def graph_view():
    return render_template("graph.html", **_common_ctx())


@bp.route("/api/graph.json")
def api_graph():
    return jsonify(models.graph_data())


@bp.route("/tags")
def tags_index():
    ctx = _common_ctx()
    ctx["tags_full"] = models.all_tags()
    return render_template("tags.html", tag=None, pages=[], **ctx)


@bp.route("/tags/<tag>")
def tag_pages(tag: str):
    ctx = _common_ctx()
    ctx["tags_full"] = models.all_tags()
    return render_template("tags.html", tag=tag, pages=models.pages_for_tag(tag), **ctx)


@bp.route("/log")
def log_view():
    page = models.get_page("log")
    if not page:
        return render_template("log.html", html="<p class='muted'>No log.md yet.</p>", **_common_ctx())
    html, _ = _render_body(page["body"])
    return render_template("log.html", html=html, page=page, **_common_ctx())


@bp.route("/index")
def page_index():
    ctx = _common_ctx()
    ctx["pages"] = models.all_pages()
    return render_template("index_all.html", **ctx)


@bp.route("/reindex", methods=["GET", "POST"])
def reindex():
    n = indexer.reindex_all(force=True)
    if request.method == "GET":
        return redirect(url_for("wiki.dashboard"))
    return jsonify({"ok": True, "indexed": n})
