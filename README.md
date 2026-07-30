# reachtim.com

A static site. Markdown and YAML in `content/`, Jinja2 templates in `templates/`,
a single `build.py` that turns one into the other and writes `dist/`. No npm, no
framework, nothing to run on the server.

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

## Build

```bash
.venv/Scripts/python build.py            # -> dist/
.venv/Scripts/python build.py --serve    # -> dist/, then http://localhost:8000
```

`dist/` is disposable and gitignored. It is also exactly what gets uploaded.

## Deploying

Upload the **contents** of `dist/` to the Porkbun static hosting root, so that
`dist/index.html` lands at `/index.html`. Every internal URL is root-absolute
(`/static/...`, `/articles/...`), so the site only works when served from a
domain root — opening `dist/index.html` off the filesystem will not load CSS.

Before uploading:

```bash
.venv/Scripts/python tools/check_build.py
```

That verifies every internal link, asset, anchor and legacy redirect resolves,
that the feed and sitemap parse, and reports which external hosts are linked.

## Adding content

**An article** — drop a Markdown file in `content/articles/` with frontmatter:

```yaml
---
title: "Reading Binary Data with Python"
slug: reading-binary-data-python     # becomes /articles/<slug>.html
legacy_slug: reading-binary-data-with-python   # optional; old Pelican URL
date: 2020-01-20
category: Python
tags: [Python, hacking]
summary: "Two ways to read binary data into a Python data structure."
math: true                            # optional; loads KaTeX on this page only
---
```

Articles sort newest-first automatically. `legacy_slug` generates a redirect stub
at `/<legacy_slug>.html` pointing at the new URL — that is how the old blog's
inbound links keep working. Omit it for anything new.

**A gallery piece** — add an entry to the relevant file in `content/galleries/`
and put the image in `static/img/<dir>/`:

```yaml
- file: crystal-19-something.jpg
  title: Descriptive label
  alt: What the image shows, for screen readers.   # required
  caption: The line printed under the plate.
```

Then re-run `tools/optimize_assets.py` (below) and `build.py`. The build fails
if a `file:` is missing from disk or an `alt:` is blank, rather than shipping a
broken or inaccessible image.

**A whole new gallery** — add a YAML file to `content/galleries/`. A gallery with
an empty `pieces:` list is skipped entirely: no page, no nav entry, no sitemap
row. That is how `crystals` sat dormant until its images arrived.

`mount:` sets the aspect ratio of the mat opening, matched to each collection's
dominant format (`4 / 3` crystals and curtains, `1 / 1` math art). Pieces are
never cropped — they are centred in the opening.

## Tools

| Script | What it does | When to run |
| --- | --- | --- |
| `tools/optimize_assets.py` | Minifies SVGs in place, renders AVIF/WebP/JPEG derivatives, writes `static/img/manifest.json` | After adding or replacing any gallery image |
| `tools/linefield.py` | Regenerates the small masthead mark into `templates/partials/` | Only if you change the mark |
| `tools/make_icons.py` | Favicon set, web manifest, and the 1200×630 social card | Only if the mark or the headline changes |
| `tools/check_build.py` | Validates `dist/` | Before every upload |
| `tools/normalize_frontmatter.py` | Converts Pelican `Key: value` headers to YAML frontmatter | Only when migrating more articles from the old blog |

`optimize_assets.py` needs Chrome or Edge to rasterize SVGs; both ship on
Windows. Without one it still minifies and still handles the raster images.

## How it is put together

Markdown goes through **python-markdown**, which is the same library Pelican used
for the original blog. That is deliberate: the articles still carry Pelican's
`:::python` / `#!python` CodeHilite fences and `{: .callout}` attr_list syntax,
and those are read natively rather than by regex that would drift.

Two things the build does that are easy to miss:

- **Headings are demoted one level.** Articles start their sections at `#`,
  because Pelican kept the title in the frontmatter. Rendering that as-is would
  put a second `<h1>` in the document, so every heading shifts down one.
- **Contents levels are rebased per article.** Some articles start sections at
  `#`, others at `##`. The contents list indents by relative depth, so both
  render identically.

Syntax highlighting is Pygments at build time; there is no client-side
highlighter. KaTeX is self-hosted and loads only on pages with `math: true`.
Fonts are self-hosted woff2. **The site makes no third-party requests at all** —
the home page is 5 requests and about 76 KB over the wire, most of it font.

## Design

Warm off-white page, dark warm ink for type, and very little else. The work
supplies the colour — photographs, drawings, syntax highlighting — and the page
stays out of its way. Code samples are the one inversion, sitting as dark blocks
on the light page.

Accents come from the art: deep teal for the technical side, deep ochre for the
art side. Both are darkened well past their source values so that small text
clears WCAG AA against this background — the same reason the Pygments comment
colour is lighter than it looks like it should be against the code block.

Ornament is deliberately minimal: a six-stroke mark beside the wordmark, and
nothing else. Type carries the page.

## Open items

- **The crystal images are the 450px copies from the Facebook album export.** If
  the camera originals turn up, drop them in over the current files and re-run
  `optimize_assets.py`; the plates would look better on a 2x display.
- Gallery titles are descriptive labels — the palette of a curtain sheet, the form
  in a crystal frame — not titles Tim gave the pieces. He has confirmed these are
  fine to keep for now.
- The curtains are generated, not hand-drawn (confirmed 2026-07-30). The
  generator is `ribbons.py` in `~/work/ribbons`, whose README documents the
  displacement-field maths, the fold thresholds, and the ten versions it took to
  stop looking like gauze. Captions are written from that.
- The math-art SVGs are Tim's own work (confirmed 2026-07-30). An earlier note in
  the repo said they were downloaded from mathart.app, which is not the case.
- Two images previously in the curtain gallery (`1vldoc6mp8dh1.jpg`,
  `uixya5fmp8dh1.jpg`) were not Tim's and have been removed. They remain in git
  history in commits before 2026-07-30.
