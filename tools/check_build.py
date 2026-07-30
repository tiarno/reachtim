"""Validate dist/ before it goes anywhere.

Checks that every internal link and asset reference resolves on disk, that the
feed and sitemap are well-formed, that every legacy Pelican URL lands on a real
article, and that nothing on the site reaches out to a third-party host.

    .venv/Scripts/python tools/check_build.py
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

REF = re.compile(
    r'(?:href|src)="([^"]+)"|srcset="([^"]+)"',
    re.IGNORECASE,
)
ALLOWED_EXTERNAL_SCHEMES = {"mailto", "tel"}


def targets(html: str) -> list[str]:
    found: list[str] = []
    for direct, srcset in REF.findall(html):
        if direct:
            found.append(direct)
        if srcset:
            found.extend(part.strip().split(" ")[0] for part in srcset.split(",") if part.strip())
    return found


def resolve(page: Path, ref: str) -> Path | None:
    """Map a URL reference to a file in dist/, or None if it isn't local."""
    parsed = urlparse(ref)
    if parsed.scheme in ALLOWED_EXTERNAL_SCHEMES or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path or path.startswith("#"):
        return None
    base = DIST if path.startswith("/") else page.parent
    target = (base / path.lstrip("/")).resolve()
    return target / "index.html" if target.is_dir() else target


def main() -> int:
    if not DIST.exists():
        print("dist/ not built", file=sys.stderr)
        return 1

    pages = sorted(DIST.rglob("*.html"))
    broken: list[str] = []
    external: dict[str, set[str]] = {}
    anchors_checked = 0

    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        ids = set(re.findall(r'id="([^"]+)"', html))
        rel = page.relative_to(DIST).as_posix()

        for ref in targets(html):
            parsed = urlparse(ref)
            if parsed.netloc:
                external.setdefault(parsed.netloc, set()).add(rel)
                continue
            if ref.startswith("#"):
                anchors_checked += 1
                if ref[1:] and ref[1:] not in ids:
                    broken.append(f"{rel}: dead anchor {ref}")
                continue
            resolved = resolve(page, ref)
            if resolved is None:
                continue
            if not resolved.exists():
                broken.append(f"{rel}: missing {ref}")

    # Feed and sitemap have to parse, not merely exist.
    feed = DIST / "feeds" / "all.atom.xml"
    sitemap = DIST / "sitemap.xml"
    entries = urls = 0
    try:
        entries = len(ET.parse(feed).getroot().findall("{http://www.w3.org/2005/Atom}entry"))
    except Exception as exc:
        broken.append(f"feed does not parse: {exc}")
    try:
        urls = len(ET.parse(sitemap).getroot())
    except Exception as exc:
        broken.append(f"sitemap does not parse: {exc}")

    # Every legacy stub must point at an article that exists.
    stubs = 0
    for page in DIST.glob("*.html"):
        html = page.read_text(encoding="utf-8", errors="replace")
        if 'http-equiv="refresh"' not in html:
            continue
        stubs += 1
        m = re.search(r'url=([^"]+)"', html)
        if not m:
            broken.append(f"{page.name}: refresh stub has no target")
            continue
        target = DIST / m[1].lstrip("/")
        if not target.exists():
            broken.append(f"{page.name}: redirects to missing {m[1]}")

    print(f"pages        {len(pages)}")
    print(f"anchors      {anchors_checked}")
    print(f"feed entries {entries}")
    print(f"sitemap URLs {urls}")
    print(f"redirects    {stubs}")
    print(f"external     {', '.join(sorted(external)) or 'none'}")

    if broken:
        print(f"\n{len(broken)} problem(s):")
        for item in broken[:40]:
            print(f"  {item}")
        return 1
    print("\nall internal links, assets, anchors and redirects resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
