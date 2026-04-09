"""Markdown rendering with wikilink support."""
import re
from typing import Callable, Optional

import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor
from xml.etree import ElementTree as etree

WIKILINK_PATTERN = r"\[\[([^\[\]\|]+?)(?:\|([^\[\]]+))?\]\]"


def _slugify_target(target: str) -> str:
    t = target.strip()
    if "/" in t:
        return "/".join(seg.strip().lower().replace(" ", "-") for seg in t.split("/"))
    return t.lower().replace(" ", "-")


class WikiLinkInlineProcessor(InlineProcessor):
    def __init__(self, pattern: str, exists_fn: Callable[[str], bool]):
        super().__init__(pattern)
        self.exists_fn = exists_fn

    def handleMatch(self, m, data):
        target = m.group(1)
        label = m.group(2) or target
        slug = _slugify_target(target)
        el = etree.Element("a")
        el.set("href", f"/w/{slug}")
        cls = "wikilink"
        if not self.exists_fn(slug):
            cls += " wikilink--broken"
            el.set("title", f"Missing page: {slug}")
        el.set("class", cls)
        el.text = label
        return el, m.start(0), m.end(0)


class MdLinkRewriter(Treeprocessor):
    """Rewrite [text](something.md) links to /w/something."""

    def run(self, root):
        for a in root.iter("a"):
            href = a.get("href", "")
            if href.endswith(".md") and not href.startswith(("http://", "https://", "/", "#")):
                slug = href[:-3].lstrip("./").lower()
                a.set("href", f"/w/{slug}")
                existing = a.get("class", "")
                a.set("class", (existing + " mdlink").strip())
        return root


class VisionExtension(Extension):
    def __init__(self, exists_fn: Callable[[str], bool], **kwargs):
        super().__init__(**kwargs)
        self.exists_fn = exists_fn

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            WikiLinkInlineProcessor(WIKILINK_PATTERN, self.exists_fn),
            "wikilink",
            175,
        )
        md.treeprocessors.register(MdLinkRewriter(md), "mdlinkrewriter", 15)


def build_markdown(exists_fn: Optional[Callable[[str], bool]] = None) -> markdown.Markdown:
    if exists_fn is None:
        exists_fn = lambda _slug: True
    return markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "footnotes",
            "sane_lists",
            "toc",
            "codehilite",
            "attr_list",
            VisionExtension(exists_fn=exists_fn),
        ],
        extension_configs={
            "toc": {"permalink": False, "toc_depth": "2-4"},
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
        },
        output_format="html",
    )


def render(body: str, exists_fn: Optional[Callable[[str], bool]] = None) -> tuple[str, list[dict]]:
    md = build_markdown(exists_fn)
    html = md.convert(body)
    toc_tokens = getattr(md, "toc_tokens", []) or []
    return html, toc_tokens
