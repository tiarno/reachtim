# Handoff

## Session Date
2026-07-30

## What Was Done

Rebuilt the site as a Python-generated static site. Previously it was 15
hand-written HTML files, each duplicating its own `<head>` and nav, with
placeholder copy and no discovery infrastructure.

- **Generator**: `build.py` + Jinja2 templates + Markdown/YAML content. See
  `README.md` for architecture, authoring and deploy.
- **Articles**: the 10 migrated pieces were re-derived from the canonical Pelican
  Markdown in `tiarno/reachtim` and now build through python-markdown, which
  reads the old CodeHilite/attr_list syntax natively. The previous session's
  one-off Node conversion script had been thrown away; conversion is now part of
  the build and reproducible.
- **Design**: palette sampled from the curtain sheets, ink/paper surfaces,
  Fraunces/Spectral/IBM Plex Mono self-hosted, and a generated ruled-line field
  as the signature element.
- **Crystals gallery added** — 18 images from the Facebook album export
  (`CrystalsandPolarizedLight`), EXIF stripped, descriptively named.
- **Curtain gallery replaced.** The two images the previous session used were
  not Tim's (`1vldoc6mp8dh1.jpg`, `uixya5fmp8dh1.jpg` — same Reddit-style ID
  suffix, both removed). Four of his own sheets from the Desktop went in
  instead. All copy claiming the curtains are "ink on paper, ruled by hand" was
  corrected: the line work is far too regular for that, and the medium is now
  left unstated pending Tim's confirmation.
- **Discovery**: canonical URLs, OG/Twitter cards, JSON-LD, sitemap, robots.txt,
  Atom feed at the old Pelican path, 404, favicon set, social card.
- **Legacy URLs**: 9 redirect stubs from the exact old Pelican slugs (read from
  each article's `Slug:` header, not guessed) to the new article URLs.

## Current State

Committed and pushed to `tiarno/reachtim` on 2026-07-30. The site builds clean
and has been verified end to end:

| Check | Result |
| --- | --- |
| Horizontal overflow, 9 pages × 375/768/1440 | none |
| Console errors | none |
| Internal links, assets, anchors, redirects | all resolve |
| WCAG AA contrast, 11 pages × 375/1440 | all text passes |
| Keyboard focus | visible on every interactive element |
| `prefers-reduced-motion` | animation disabled, static final state |
| Third-party requests | none |
| Home page weight | 5 requests, ~88 KB gzipped |
| Feed / sitemap | parse; 10 entries, 17 URLs |

Bugs found and fixed during verification, worth knowing about because they were
all silent:

- Articles whose sections start at `#` were losing **every** contents entry
  (`toc_depth` excluded level 1). `pdfcheck` had 0 of 5, `pdfmanip` 11 of 17.
- Frontmatter summaries rendered raw Markdown (`*n*`) in the page.
- KaTeX display math and long inline `<code>` pushed the document wider than a
  phone screen.
- Several colours failed AA: `--fg-faint` at 3.16:1 carried every date and
  caption; Pygments comment and tag tokens were 3.3–3.9:1.

## What's Blocked

- **Deploy is manual and not done.** Upload the contents of `dist/` to Porkbun
  static hosting (see README). `reachtim.com` is currently a parked Porkbun
  placeholder, so this is the step that makes the site live. Tim is holding off
  until he's ready.
- **The old Pelican blog is preserved on the `pelican-archive` branch** of
  `tiarno/reachtim` (19 articles, full history). `master` now holds this site;
  the two histories are unrelated, so master was force-pushed after the archive
  branch was created and verified.

## Next Steps

1. Review the site locally: `.venv/Scripts/python build.py --serve`.
2. Confirm the curtain medium (plotter? rendered?) so the captions and the about
   page can say what it actually is.
3. Upload `dist/` to Porkbun when ready to go live.
4. If the original crystal photographs turn up, drop them in over the 450px
   Facebook copies and re-run `tools/optimize_assets.py`.

## Notes of Record

- **The math-art SVGs are Tim's own work** (confirmed 2026-07-30). The previous
  handoff recorded them as downloaded from mathart.app; that was wrong, and the
  note is corrected here so it does not get re-raised.
- Curtain titles "Ember" and "Undertow" from the previous session were invented,
  not supplied by Tim. Those images are gone entirely; the four replacements use
  descriptive palette labels, which Tim has confirmed are fine for now.
- The two removed curtain images remain in git history in commits before
  2026-07-30. Removing them from history would need a rewrite and a force-push;
  not done, and not obviously worth it.
- Only `padpages` uses LaTeX math — the previous handoff said two articles.
- 9 of the 19 old blog articles remain unmigrated, by choice. The three drafts
  among them (`scapy_intro`, `bpf_scapy`, `ipv4_v6`) are network-security pieces
  that were never published on the old blog.
