"""Shrink the gallery images and write the manifest build.py reads.

Three jobs:

1. Minify the math-art SVGs in place. They carry ~120,000 coordinates at 13-14
   decimal places against a 1536px viewBox, which is about twelve significant
   digits more than a screen can show. Rounding to one decimal is visually
   lossless and cuts the files by roughly 4x.

2. Rasterize every piece into AVIF and WebP derivatives for the gallery grid.
   This matters most for the SVGs: each one carries an feTurbulence paper-grain
   filter, and asking a browser to run twelve fractal-noise filters over twelve
   1536px canvases to draw twelve thumbnails is slow on any machine. A raster has
   the grain already baked in. The full vector is still linked from each plate.

3. Write static/img/manifest.json — dimensions and srcset for each piece, so
   templates can size images exactly and nothing reflows during load.

    .venv/Scripts/python tools/optimize_assets.py

Needs Chrome or Edge for SVG rasterization; both ship on Windows. Without one,
SVG minification and the JPEG derivatives still run.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "static" / "img"

# Widths to emit. A plate is never wider than 30rem (480px), so 960 already
# covers a 2x display and anything larger would be generated, uploaded, and
# never requested. Full resolution stays available as the linked original.
WIDTHS = [480, 960]
QUALITY = {"avif": 52, "webp": 78, "jpeg": 82}

# One decimal against a 1536px viewBox is a tenth of a pixel.
SVG_PRECISION = 1
FLOAT = re.compile(r"-?\d+\.\d+")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

GALLERY_DIRS = ["curtains", "mathart", "crystals"]


def find_chrome() -> Path | None:
    for candidate in CHROME_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return path
    return shutil.which("chrome") and Path(shutil.which("chrome"))  # type: ignore[return-value]


def minify_svg(path: Path) -> tuple[int, int]:
    """Round coordinates and collapse whitespace. Returns (before, after)."""
    raw = path.read_text(encoding="utf-8")
    before = len(raw.encode("utf-8"))

    def shorten(m: re.Match[str]) -> str:
        value = round(float(m.group(0)), SVG_PRECISION)
        # Drop a trailing .0 — it is two bytes times a hundred thousand.
        return str(int(value)) if value == int(value) else str(value)

    out = FLOAT.sub(shorten, raw)
    out = re.sub(r">\s+<", "><", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    path.write_text(out, encoding="utf-8")
    return before, len(out.encode("utf-8"))


def svg_viewbox(path: Path) -> tuple[int, int]:
    head = path.read_text(encoding="utf-8")[:600]
    if m := re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head):
        return int(float(m[1])), int(float(m[2]))
    if m := re.search(r'width="(\d+)"[^>]*height="(\d+)"', head):
        return int(m[1]), int(m[2])
    return 1536, 1536


def rasterize_svg(chrome: Path, svg: Path, out: Path, width: int, height: int) -> bool:
    """Render an SVG to PNG with headless Chrome."""
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            str(chrome),
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--user-data-dir={profile}",
            f"--window-size={width},{height}",
            f"--screenshot={out}",
            svg.resolve().as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=120)
    if not out.exists():
        print(f"    ! rasterize failed: {result.stderr.decode(errors='replace')[:200]}")
        return False
    return True


def derivatives(source: Image.Image, stem: str, out_dir: Path) -> dict:
    """Write AVIF/WebP/JPEG at each width; return manifest source entries."""
    out_dir.mkdir(parents=True, exist_ok=True)
    src_w, src_h = source.size
    widths = [w for w in WIDTHS if w <= src_w] or [src_w]

    made: dict[str, list[str]] = {"avif": [], "webp": [], "jpeg": []}
    for width in widths:
        height = round(width * src_h / src_w)
        resized = source.resize((width, height), Image.LANCZOS)
        for fmt, ext in (("avif", "avif"), ("webp", "webp"), ("jpeg", "jpg")):
            name = f"{stem}-{width}.{ext}"
            resized.save(out_dir / name, format=fmt.upper(), quality=QUALITY[fmt])
            made[fmt].append(f"/static/img/{out_dir.parent.name}/d/{name} {width}w")

    return {
        "width": src_w,
        "height": src_h,
        "sources": [
            {"type": "image/avif", "srcset": ", ".join(made["avif"])},
            {"type": "image/webp", "srcset": ", ".join(made["webp"])},
        ],
        "fallback": {
            "src": made["jpeg"][-1].split(" ")[0],
            "srcset": ", ".join(made["jpeg"]),
        },
    }


def main() -> int:
    chrome = find_chrome()
    if chrome:
        print(f"rasterizer: {chrome.name}")
    else:
        print("rasterizer: none found — SVG thumbnails will be skipped")

    manifest: dict[str, dict] = {}
    saved_before = saved_after = 0

    for gallery in GALLERY_DIRS:
        gdir = IMG / gallery
        if not gdir.is_dir():
            continue
        sources = sorted(
            p for p in gdir.iterdir() if p.suffix.lower() in {".svg", ".jpg", ".jpeg", ".png"}
        )
        if not sources:
            continue
        print(f"\n{gallery}/")
        out_dir = gdir / "d"

        for src in sources:
            key = f"{gallery}/{src.name}"

            if src.suffix.lower() == ".svg":
                before, after = minify_svg(src)
                saved_before += before
                saved_after += after
                print(f"  {src.name:26} {before / 1024:7.0f} KB -> {after / 1024:6.0f} KB")

                if not chrome:
                    continue
                w, h = svg_viewbox(src)
                with tempfile.TemporaryDirectory() as tmp:
                    png = Path(tmp) / "shot.png"
                    if not rasterize_svg(chrome, src, png, w, h):
                        continue
                    with Image.open(png) as im:
                        manifest[key] = derivatives(
                            im.convert("RGB"), src.stem, out_dir
                        )
            else:
                with Image.open(src) as im:
                    manifest[key] = derivatives(im.convert("RGB"), src.stem, out_dir)
                print(f"  {src.name:26} {im.size[0]}x{im.size[1]} derivatives written")

    (IMG / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    if saved_before:
        print(
            f"\nSVG minify: {saved_before / 1024 / 1024:.2f} MB -> "
            f"{saved_after / 1024 / 1024:.2f} MB "
            f"({100 - saved_after * 100 / saved_before:.0f}% smaller)"
        )
    print(f"manifest: {len(manifest)} pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
