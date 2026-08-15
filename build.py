#!/usr/bin/env python
"""Static site generator for reachtim.com.

Reads Markdown/YAML out of content/, renders it through the Jinja2 templates in
templates/, and writes a complete static site to dist/. That directory is what
gets uploaded to the host — there is no server-side anything.

    .venv/Scripts/python build.py            build to dist/
    .venv/Scripts/python build.py --serve    build, then serve dist/ on :8000

Markdown is handled by python-markdown, which is the same library Pelican used
for the original blog. That is deliberate: the old `:::python` / `#!python`
CodeHilite fences and `{: .callout}` attr_list syntax in content/articles/ are
read natively, with no regex preprocessing to drift out of sync.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

# Articles were written for Pelican, whose images lived one level up.
LEGACY_IMAGE_PREFIX = "../images/"
BLOG_IMAGE_PATH = "/static/img/blog/"

# The old blog printed a bold "Table of Contents" label above a [TOC] marker.
# Both are dropped: the template builds its own contents nav from toc_tokens.
TOC_NOISE = re.compile(r"^\s*(\*\*Table of Contents\*\*|\[TOC\])\s*$", re.MULTILINE)

# Article bodies start their headings at `#`, which would collide with the page
# title. Every heading is demoted one level. Safe to do on rendered HTML: code
# samples are escaped inside <pre>, and raw <th>/<table> passthroughs don't match.
HEADING_TAG = re.compile(r"<(/?)h([1-6])\b")


INLINE_MD = re.compile(r"[*_`]")


def inline_markdown(md: markdown.Markdown, text: str) -> str:
    """Render a one-line field (a summary) without wrapping it in <p>."""
    md.reset()
    return md.convert(text).removeprefix("<p>").removesuffix("</p>").strip()


def plain_text(text: str) -> str:
    """Strip Markdown emphasis for meta tags and the feed, which want no markup."""
    return INLINE_MD.sub("", text)


@dataclass
class Article:
    slug: str
    title: str
    summary: str
    summary_html: str
    category: str
    tags: list[str]
    date: date
    body: str
    toc: list[dict]
    math: bool = False
    legacy_slug: str | None = None

    @property
    def url(self) -> str:
        return f"/articles/{self.slug}.html"


@dataclass
class Gallery:
    slug: str
    title: str
    summary: str
    lane: str
    order: int
    dir: str
    mount: str
    pieces: list[dict] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"/art/{self.slug}.html"


@dataclass
class Page:
    slug: str
    title: str
    headline: str
    description: str
    template: str
    body: str
    lane: str | None = None

    @property
    def url(self) -> str:
        return "/" if self.slug == "index" else f"/{self.slug}.html"


def make_markdown() -> markdown.Markdown:
    """A converter configured for the old blog's Markdown dialect."""
    return markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "attr_list",
            "def_list",
            "footnotes",
            "sane_lists",
            "smarty",
            "md_in_html",
            CodeHiliteExtension(css_class="highlight", guess_lang=False),
            # 1-4, not 2-4: these articles came from Pelican, where the page
            # title lived in the frontmatter, so a `#` in the body is a section
            # heading rather than the document title. Excluding level 1 dropped
            # every section from articles written that way.
            TocExtension(permalink=False, toc_depth="1-4"),
        ],
        output_format="html",
    )


def split_frontmatter(text: str, source: Path) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError(f"{source}: missing YAML frontmatter")
    _, raw, body = text.split("---", 2)
    return yaml.safe_load(raw) or {}, body.strip()


def flatten_toc(tokens: list[dict]) -> list[dict]:
    """toc_tokens is nested; the template wants a flat list with levels.

    Levels are rebased so the shallowest heading in the article is level 1,
    whether its author started sections at `#` or at `##`. The contents list
    then indents by relative depth instead of by absolute heading tag.
    """

    def walk(nodes: list[dict]) -> list[dict]:
        out: list[dict] = []
        for token in nodes:
            # smarty renders headings with literal entities (Let&rsquo;s), and
            # this string goes through Jinja's autoescape same as any other
            # value, which would double-escape the & into &amp;rsquo;.
            out.append(
                {
                    "id": token["id"],
                    "name": html.unescape(token["name"]),
                    "level": token["level"],
                }
            )
            out.extend(walk(token.get("children", [])))
        return out

    items = walk(tokens)
    if not items:
        return items
    shallowest = min(item["level"] for item in items)
    for item in items:
        item["level"] -= shallowest - 1
    return items


def render_body(md: markdown.Markdown, text: str) -> tuple[str, list[dict]]:
    md.reset()
    html = md.convert(TOC_NOISE.sub("", text))
    html = HEADING_TAG.sub(lambda m: f"<{m[1]}h{min(int(m[2]) + 1, 6)}", html)
    html = html.replace(LEGACY_IMAGE_PREFIX, BLOG_IMAGE_PATH)
    return html, flatten_toc(getattr(md, "toc_tokens", []))


def load_articles(md: markdown.Markdown) -> list[Article]:
    articles: list[Article] = []
    for path in sorted((CONTENT / "articles").glob("*.md")):
        meta, text = split_frontmatter(path.read_text(encoding="utf-8"), path)
        body, toc = render_body(md, text)
        summary = meta.get("summary", "")
        articles.append(
            Article(
                slug=meta["slug"],
                title=meta["title"],
                summary=plain_text(summary),
                summary_html=inline_markdown(md, summary),
                category=meta.get("category", "Notes"),
                tags=meta.get("tags") or [],
                date=meta["date"],
                body=body,
                toc=toc,
                math=bool(meta.get("math")),
                legacy_slug=meta.get("legacy_slug"),
            )
        )
    articles.sort(key=lambda a: a.date, reverse=True)
    return articles


def load_galleries() -> list[Gallery]:
    galleries: list[Gallery] = []
    for path in sorted((CONTENT / "galleries").glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        pieces = data.get("pieces") or []
        if not pieces:
            # An empty gallery is a room with nothing in it. Skip it entirely:
            # no page, no link in the art index, no sitemap entry.
            print(f"  skip {path.name} (no pieces yet)")
            continue

        # A typo in a filename would otherwise ship as a broken image, and a
        # missing alt as an inaccessible one. Fail the build instead.
        img_dir = STATIC / "img" / data.get("dir", data["slug"])
        for piece in pieces:
            if not (img_dir / piece["file"]).exists():
                raise FileNotFoundError(
                    f"{path.name}: {piece['file']} not found in {img_dir}"
                )
            if not piece.get("alt", "").strip():
                raise ValueError(f"{path.name}: {piece['file']} has no alt text")
        galleries.append(
            Gallery(
                slug=data["slug"],
                title=data["title"],
                summary=data.get("summary", "").strip(),
                lane=data.get("lane", "art"),
                order=int(data.get("order", 99)),
                dir=data.get("dir", data["slug"]),
                # Aspect ratio of the mat opening. Each collection has its own
                # natural format, so a single ratio would waste paper on two of
                # the three.
                mount=str(data.get("mount", "1 / 1")),
                pieces=pieces,
            )
        )
    galleries.sort(key=lambda g: g.order)
    return galleries


def load_pages(md: markdown.Markdown) -> list[Page]:
    pages: list[Page] = []
    for path in sorted((CONTENT / "pages").glob("*.md")):
        meta, text = split_frontmatter(path.read_text(encoding="utf-8"), path)
        body, _ = render_body(md, text)
        pages.append(
            Page(
                slug=meta["slug"],
                title=meta["title"],
                headline=meta.get("headline", meta["title"]),
                description=(meta.get("description") or "").strip(),
                template=meta.get("template", "page"),
                body=body,
                lane=meta.get("lane"),
            )
        )
    return pages


def load_manifest() -> dict:
    """Image dimensions and derivative sets, written by tools/optimize_assets.py.

    Absent on a fresh checkout — the templates fall back to the original file
    with no srcset, so the build always works.
    """
    path = STATIC / "img" / "manifest.json"
    if not path.exists():
        print("  no image manifest — run tools/optimize_assets.py for srcset")
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(*, clean: bool = True) -> None:
    site = yaml.safe_load((CONTENT / "site.yml").read_text(encoding="utf-8"))
    md = make_markdown()

    print("reading content")
    articles = load_articles(md)
    galleries = load_galleries()
    pages = load_pages(md)
    manifest = load_manifest()
    print(f"  {len(articles)} articles, {len(galleries)} galleries, {len(pages)} pages")

    if clean and DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["datefmt"] = lambda d, fmt="%B %-d, %Y": d.strftime(
        fmt.replace("%-d", str(d.day))
    )

    built: list[tuple[str, date | None]] = []
    shared = {
        "site": site,
        "articles": articles,
        "galleries": galleries,
        "manifest": manifest,
        "build_time": datetime.now(timezone.utc),
    }

    print("rendering")
    for page in pages:
        html = env.get_template(f"{page.template}.html.j2").render(
            page=page, current=page.slug, **shared
        )
        target = "index.html" if page.slug == "index" else f"{page.slug}.html"
        write(DIST / target, html)
        built.append((page.url, None))

    article_tmpl = env.get_template("article.html.j2")
    for article in articles:
        write(
            DIST / "articles" / f"{article.slug}.html",
            article_tmpl.render(page=article, current="tech", **shared),
        )
        built.append((article.url, article.date))

    gallery_tmpl = env.get_template("gallery.html.j2")
    for gallery in galleries:
        write(
            DIST / "art" / f"{gallery.slug}.html",
            gallery_tmpl.render(page=gallery, current="art", **shared),
        )
        built.append((gallery.url, None))

    # Old Pelican URLs were flat /{slug}.html. This host serves no redirects, so
    # each one gets a stub carrying rel=canonical plus a meta refresh.
    redirect_tmpl = env.get_template("redirect.html.j2")
    redirects = 0
    for article in articles:
        if not article.legacy_slug or article.legacy_slug == article.slug:
            continue
        write(
            DIST / f"{article.legacy_slug}.html",
            redirect_tmpl.render(target=article.url, page=article, **shared),
        )
        redirects += 1

    write(
        DIST / "sitemap.xml",
        env.get_template("sitemap.xml.j2").render(urls=built, **shared),
    )
    write(
        DIST / "feeds" / "all.atom.xml",
        env.get_template("atom.xml.j2").render(**shared),
    )
    write(DIST / "robots.txt", env.get_template("robots.txt.j2").render(**shared))
    write(
        DIST / "404.html",
        env.get_template("404.html.j2").render(current=None, **shared),
    )

    shutil.copytree(STATIC, DIST / "static", dirs_exist_ok=True)

    total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(
        f"wrote {len(built)} pages + {redirects} redirect stubs "
        f"to dist/ ({total / 1024:.0f} KB)"
    )


def serve(port: int) -> None:
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(DIST))
    print(f"serving dist/ at http://localhost:{port}  (ctrl-c to stop)")
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="serve dist/ after build")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    try:
        build()
    except Exception as exc:  # surface the failing file, not a bare traceback
        print(f"build failed: {exc}", file=sys.stderr)
        raise

    if args.serve:
        serve(args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
