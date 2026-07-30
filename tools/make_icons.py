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

PAGE = (247, 244, 236)
INK = (33, 32, 28)
MUTED = (85, 80, 74)
OCHRE = (125, 90, 15)
TEAL = (28, 86, 91)

FAVICON_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="4" fill="#21201c"/>
  <g fill="none" stroke="#f7f4ec" stroke-width="1.6" stroke-linecap="round">
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
    """Light strokes on ink.

    Inverted relative to the site on purpose: a browser tab strip is usually
    light, so a light icon disappears into it. Ink reads on either.
    """
    img = Image.new("RGB", (size, size), INK)
    d = ImageDraw.Draw(img)
    pad = size * pad_ratio
    span = size - 2 * pad
    width = max(1, round(size / 20))
    for i in range(6):
        x = pad + span * (i / 5) ** 1.6
        d.line([(x, pad), (x, size - pad)], fill=PAGE, width=width)
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
    """1200x630 share card. Type on the page colour, no ornament."""
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), PAGE)
    d = ImageDraw.Draw(img)

    title = load_font("fraunces-display.woff2", 82)
    body = load_font("spectral-regular.woff2", 30)
    meta = load_font("plexmono-regular.woff2", 23)

    d.text((78, 150), "REACHTIM", font=meta, fill=MUTED)
    d.text((78, 214), "Tim Arnold", font=title, fill=INK)
    d.text(
        (78, 330),
        "Python, the insides of PDF and LaTeX,",
        font=body,
        fill=MUTED,
    )
    d.text((78, 372), "and a pile of pictures I made.", font=body, fill=MUTED)

    d.line([(78, 456), (1122, 456)], fill=(33, 30, 26, 40), width=1)
    d.text((78, 482), "WRITING", font=meta, fill=TEAL)
    d.text((236, 482), "PICTURES", font=meta, fill=OCHRE)

    img.save(IMG / "og-default.png", optimize=True)


def write_manifest() -> None:
    (ICONS / "manifest.webmanifest").write_text(
        json.dumps(
            {
                "name": "reachtim",
                "short_name": "reachtim",
                "start_url": "/",
                "display": "browser",
                "background_color": "#f7f4ec",
                "theme_color": "#f7f4ec",
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
