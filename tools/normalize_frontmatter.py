"""Convert Pelican-style article frontmatter to YAML frontmatter.

The articles in content/articles/ came from the old Pelican blog, which used
`Key: value` headers. This rewrites them in place as YAML frontmatter and adds
two fields the build needs:

    slug         the article's URL name on this site
    legacy_slug  the URL Pelican published it under, so build.py can emit a
                 redirect stub and keep old inbound links working

Run once per batch of newly migrated articles:

    .venv/Scripts/python tools/normalize_frontmatter.py
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ARTICLES = Path(__file__).resolve().parent.parent / "content" / "articles"

# source stem -> the slug this site publishes it under
NEW_SLUGS = {
    "bottle": "bam-web-framework",
    "context_manager": "contextmanager-decorator",
    "ctype_struct": "reading-binary-data-python",
    "html2latex": "include-html-in-latex",
    "keywords_xsl": "keywords-metadata-index-terms",
    "padpages": "pad-pdf-to-n-pages",
    "pdfcheck": "testing-pdfs-with-python",
    "pdfmanip": "manipulate-pdfs-with-python",
    "psutil1": "psutil-mongodb-monitoring",
    "statrep_latex": "sas-latex-statrep",
}

MONTHS = {
    m.lower(): i
    for i, m in enumerate(
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), start=1
    )
}


def pelican_slugify(title: str) -> str:
    """Reproduce Pelican's default slug: lowercase, non-alphanumerics to hyphens."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"[-\s]+", "-", slug).strip("-")


def parse_date(raw: str) -> date:
    """Handle every format the old blog used: 2014-Sep-29, 01-22-2020, 2019-May-06."""
    raw = raw.strip()
    if m := re.fullmatch(r"(\d{4})-([A-Za-z]{3})-(\d{1,2})", raw):
        return date(int(m[1]), MONTHS[m[2].lower()], int(m[3]))
    if m := re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{4})", raw):
        return date(int(m[3]), int(m[1]), int(m[2]))
    if m := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", raw):
        return date(int(m[1]), int(m[2]), int(m[3]))
    raise ValueError(f"unrecognized date: {raw!r}")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Pelican headers run from the top until the first blank line."""
    meta: dict[str, str] = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            return meta, "\n".join(lines[i + 1 :]).lstrip("\n")
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip()
    return meta, ""


def quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalize(path: Path) -> None:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    if not meta.get("title"):
        raise ValueError(f"{path.name}: no Title header — already normalized?")

    title = meta["title"].strip()
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]

    fields = [
        f"title: {quote(title)}",
        f"slug: {NEW_SLUGS[path.stem]}",
        f"legacy_slug: {meta.get('slug') or pelican_slugify(title)}",
        f"date: {parse_date(meta['date']).isoformat()}",
        f"category: {meta.get('category', 'Notes')}",
        f"tags: [{', '.join(tags)}]",
        f"summary: {quote(meta.get('summary', '').rstrip('.') + '.')}",
    ]
    # Only padpages uses LaTeX math; the flag keeps KaTeX off every other page.
    if "$$" in body or re.search(r"(?<!\\)\$[^$\n]+\$", body):
        fields.append("math: true")

    path.write_text(
        "---\n" + "\n".join(fields) + "\n---\n\n" + body.strip() + "\n",
        encoding="utf-8",
    )
    print(f"  {path.name:22} -> {NEW_SLUGS[path.stem]}")


def main() -> int:
    files = sorted(ARTICLES.glob("*.md"))
    if not files:
        print(f"no articles in {ARTICLES}", file=sys.stderr)
        return 1
    print(f"normalizing {len(files)} articles")
    for path in files:
        normalize(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
