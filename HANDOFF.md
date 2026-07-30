# Handoff

## Session Date
2026-07-30

## What Was Done

**The site is live at <https://reachtim.com>.** It was 15 hand-written HTML files
with placeholder copy; it is now a Python-generated static site, deployed.

- **Generator** — `build.py` + Jinja2 over Markdown/YAML in `content/`. Markdown
  goes through python-markdown, the same library Pelican used, so the old
  `:::python` CodeHilite fences and `{: .callout}` syntax parse natively. The
  previous session's one-off Node converter had been thrown away; conversion is
  now part of the build. See `README.md` for architecture and authoring.
- **Design** — warm light page, dark ink type, Fraunces / Spectral / IBM Plex
  Mono self-hosted. Built dark around a generated line field first; Tim asked
  for light, less line-drawing emphasis and a more personal voice, so the field
  and lane motifs are gone, all copy is first person, and only a six-stroke
  masthead mark remains.
- **Content** — 11 articles (10 migrated from the old Pelican blog + a new
  LoRecon piece), 3 galleries: curtains (4), math art (12), crystals (18).
  Portrait added to the landing page.
- **Curtain gallery replaced.** The two images the previous session used were
  not Tim's (`1vldoc6mp8dh1.jpg`, `uixya5fmp8dh1.jpg`). Four of his own sheets
  replaced them. They are **generated**, not hand-drawn — `ribbons.py` in
  `~/work/ribbons`; captions written from that README.
- **Discovery** — canonical URLs, OG/Twitter cards, JSON-LD, sitemap,
  robots.txt, Atom feed at the old Pelican path, 404, favicon set, social card,
  and 9 redirect stubs from the exact old Pelican slugs.
- **Deploy** — `tools/deploy.py`, FTPS to Porkbun, credentials from the
  environment only.

## Current State

Live, and pushed to `tiarno/reachtim`. Five commits: `6988472` → `1bb6c8d`.

| Check | Result |
| --- | --- |
| Live pages, CSS, sitemap, robots, feed, legacy redirects | all 200 |
| Horizontal overflow, 375 / 768 / 1440 | none |
| Console errors | none |
| Internal links, assets, anchors, redirects | all resolve |
| WCAG AA contrast, 375 / 1440 | all text passes |
| Third-party requests | none |
| Home page | 5 requests, ~76 KB gzipped (mostly font) |

Bugs found during verification, all of which were silent:

- Articles whose sections start at `#` lost **every** contents entry
  (`toc_depth` excluded level 1). `pdfcheck` had 0 of 5, `pdfmanip` 11 of 17.
- Gallery mats were not uniform — `aspect-ratio` was overridden because a
  percentage height cannot resolve against a height derived from the width.
  Openings ranged 300–583px in one gallery.
- Frontmatter summaries rendered raw Markdown (`*n*`) on the page.
- KaTeX display math and long inline `<code>` overflowed narrow screens.
- Several colours failed AA, including the one carrying every date and caption.

## What's Blocked

- **Something syncs the GitHub repo into the web root.** The root held 80 files
  that were not part of any site — this repo's source, the old Pelican source,
  and the three never-published drafts (`scapy_intro.md`, `bpf_scapy.md`,
  `ipv4_v6.md`) — carrying that day's timestamps. Looks like Porkbun's
  "connect to a GitHub repository" feature. `dist/` is gitignored, so that sync
  can never produce a working site, and **the next push may undo the deploy**.
  Tim needs to check Static Hosting settings and disconnect it. Files are pruned
  for now and all recoverable from git.

## Next Steps

1. Confirm the GitHub → Porkbun sync is off, then re-check the live site.
2. Redeploy after any content change:
   `check_build.py`, then `deploy.py --prune` (see README for the env vars).
3. If the original crystal photographs turn up, drop them in over the 450px
   Facebook copies and re-run `tools/optimize_assets.py`.

## Key Parameters/Settings

- Branch `master` on `tiarno/reachtim`; the old Pelican blog is intact on
  `pelican-archive` (19 articles, full history) — master was force-pushed only
  after that branch was created and verified.
- FTP: host `pixie-ss1-ftp.porkbun.com` (leading `p` — `ixie-…` is a typo trap
  that *resolves* anyway via wildcard DNS and then times out), user
  `reachtim.com`, password from the Porkbun panel. **Not stored in this repo —
  it is public.**
- Porkbun requires TLS, and its vsFTPd has no `MLSD`, so remote listing parses
  unix `LIST`. Transfers reset often; `deploy.py` retries and skips files whose
  remote size matches.
- Build: `.venv/Scripts/python build.py [--serve]`.

## Files Changed

311 files vs. the session's starting commit (`a7ea3b6`). Structurally:

- Added: `build.py`, `templates/`, `content/`, `tools/` (`deploy.py`,
  `optimize_assets.py`, `check_build.py`, `linefield.py`, `make_icons.py`,
  `normalize_frontmatter.py`), `README.md`, `requirements.txt`, `.gitignore`
- Replaced: `assets/` → `static/img/`; hand-written `*.html` and `styles.css`
  deleted in favour of generated output
- `dist/` is build output and gitignored

## Notes of Record

- **The math-art SVGs are Tim's own work** (confirmed 2026-07-30) — an earlier
  note wrongly recorded them as downloaded from mathart.app.
- Gallery titles are descriptive labels, not titles Tim gave the pieces. He has
  confirmed they are fine to keep.
- The two removed curtain images remain in git history before 2026-07-30.
  Removing them would need a history rewrite; not done.
- Only `padpages` uses LaTeX math — an earlier note said two articles.
- 9 of the 19 old blog articles remain unmigrated by choice.
