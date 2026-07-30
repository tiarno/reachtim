"""Generate the favicon set and the social-card image.

Both reuse the site's mark — ruled strokes tightening left to right — so the tab
icon, the share card and the masthead are the same drawing at three sizes.

    .venv/Scripts/python tools/make_icons.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "static" / "icons"
IMG = ROOT / "static" / "img"
FONTS = ROOT / "static" / "fonts"

INK = (28, 26, 23)
PAPER = (237, 231, 218)
OCHRE = (216, 163, 43)
TEAL = (46, 127, 134)

FAVICON_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="4" fill="#1c1a17"/>
  <g fill="none" stroke="#ede7da" stroke-width="1.6" stroke-linecap="round">
{strokes}
  </g>
</svg>
"""


def stroke_positions(n: int = 6, span: float = 22.0, start: float = 5.0) -> list[float]:
    """Pitch tightens toward the right, the same easing as the masthead rule."""
    return [start + span * (i / (n - 1)) ** 1.6 for i in range(n)]


def write_favicon_svg() -> None:
    lines = [
        f'    <path d="M{x:.1f},7L{x:.1f},25"/>' for x in stroke_positions()
    ]
    (ICONS / "favicon.svg").write_text(
        FAVICON_SVG.format(strokes="\n".join(lines)), encoding="utf-8"
    )


def draw_mark(size: int, pad_ratio: float = 0.22) -> Image.Image:
    img = Image.new("RGB", (size, size), INK)
    d = ImageDraw.Draw(img)
    pad = size * pad_ratio
    span = size - 2 * pad
    width = max(1, round(size / 20))
    for i in range(6):
        x = pad + span * (i / 5) ** 1.6
        d.line([(x, pad), (x, size - pad)], fill=PAPER, width=width)
    return img


def write_rasters() -> None:
    # .ico carries the sizes Windows and older browsers ask for.
    base = draw_mark(256)
    base.save(
        ICONS / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    draw_mark(180, pad_ratio=0.2).save(ICONS / "apple-touch-icon.png")
    for px in (192, 512):
        draw_mark(px).save(ICONS / f"icon-{px}.png")


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except OSError:
        return ImageFont.load_default(size)


def write_og_card() -> None:
    """1200x630 share card: the line field, the name, the two lanes."""
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)

    # The signature field, straight at the left and folding toward the right.
    n = 74
    for i in range(n):
        y0 = h * (i + 0.5) / n
        phase = (i / n) * math.tau * 1.6
        pts = []
        for s in range(61):
            t = s / 60
            disorder = t * t * (3 - 2 * t)
            fold = math.sin(t * math.tau * 1.15 + phase * 0.35)
            swell = math.sin(t * math.pi * 0.85 + phase * 0.12)
            amp = 108 * disorder
            y = y0 + fold * amp * 0.42 + swell * amp * 0.28
            y += 20 * disorder * math.sin(phase + t * math.pi)
            pts.append((t * w, y))
        # Dim, so the type stays legible on top.
        d.line(pts, fill=(58, 54, 48), width=1, joint="curve")

    title = load_font("fraunces-display.woff2", 78)
    meta = load_font("plexmono-regular.woff2", 24)

    d.text((72, 236), "Line work,", font=title, fill=PAPER)
    d.text((72, 322), "in two registers.", font=title, fill=PAPER)
    d.text((72, 168), "REACHTIM  ·  TIM ARNOLD", font=meta, fill=(169, 161, 150))

    d.text((72, 470), "TECHNICAL", font=meta, fill=TEAL)
    d.text((262, 470), "ART", font=meta, fill=OCHRE)
    d.line([(72, 452), (1128, 452)], fill=(52, 48, 42), width=1)

    img.save(IMG / "og-default.png", optimize=True)
    return None


def write_manifest() -> None:
    (ICONS / "manifest.webmanifest").write_text(
        json.dumps(
            {
                "name": "reachtim",
                "short_name": "reachtim",
                "start_url": "/",
                "display": "browser",
                "background_color": "#1c1a17",
                "theme_color": "#1c1a17",
                "icons": [
                    {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                    {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    ICONS.mkdir(parents=True, exist_ok=True)
    write_favicon_svg()
    write_rasters()
    write_manifest()
    write_og_card()
    for path in sorted(ICONS.iterdir()):
        print(f"  {path.name:26} {path.stat().st_size / 1024:6.1f} KB")
    og = IMG / "og-default.png"
    print(f"  {og.name:26} {og.stat().st_size / 1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
