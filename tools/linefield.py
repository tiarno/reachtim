"""Generate the site's ruled-line ornaments.

The curtain drawings in the art gallery are built from several hundred ruled
parallel strokes, where the spacing alone describes the drape. This produces the
same mark digitally, in the site's two registers:

    partials/_linefield_home.svg   the hero field. Strokes start straight and
                                   evenly pitched at the left edge and
                                   progressively bow, crowd and fold toward the
                                   right — the technical lane sits under the
                                   ordered edge, the art lane under the drape.
    partials/_register_tech.svg    four strokes, straight and evenly spaced
    partials/_register_art.svg     the same four, bowed and unevenly spaced
    partials/_rule.svg             a short masthead rule

Output goes into templates/partials/ so the templates can inline it (an inline
SVG inherits currentColor and can be animated; an <img> can do neither).

    .venv/Scripts/python tools/linefield.py
"""

from __future__ import annotations

import math
from pathlib import Path

PARTIALS = Path(__file__).resolve().parent.parent / "templates" / "partials"

# Viewbox for the hero field. Wide and shallow — it sits behind the headline.
W, H = 1200, 520
STROKES = 110
# Knots per stroke. The stroke is a smooth wave, so a handful of Catmull-Rom
# spans reproduces it exactly enough — and 110 strokes of dense polyline would
# be a quarter-megabyte of inline SVG.
KNOTS = 9


def ease(t: float) -> float:
    """Smoothstep. Keeps the straight-to-drape transition from having a seam."""
    return t * t * (3 - 2 * t)


def sample(i: int, n: int, t: float) -> tuple[float, float]:
    """Position of stroke `i` at `t` along the width.

    `disorder` ramps from 0 to 1 across the width, and every departure from a
    straight line is scaled by it: amplitude, phase drift, and the vertical
    crowding that makes strokes pool into folds.
    """
    y0 = H * (i + 0.5) / n  # even pitch at rest
    # Each stroke gets its own phase so the field reads as fabric, not a moire.
    phase = (i / n) * math.tau * 1.6
    disorder = ease(t)

    # Two folds across the sheet, plus a slower swell.
    fold = math.sin(t * math.tau * 1.15 + phase * 0.35)
    swell = math.sin(t * math.pi * 0.85 + phase * 0.12)
    amplitude = 96 * disorder

    # Strokes crowd toward the folds: the local gradient of the fold curve
    # squeezes neighbouring strokes together, which is what reads as shadow.
    crowd = 26 * disorder * math.cos(t * math.tau * 1.15 + phase * 0.35)
    drift = 18 * disorder * math.sin(phase + t * math.pi)

    y = y0 + fold * amplitude * 0.42 + swell * amplitude * 0.28
    y += crowd * (0.5 - abs(0.5 - (i / n))) * 2 + drift
    return t * W, y


def stroke_path(i: int, n: int) -> str:
    """One stroke as a Catmull-Rom spline written out as cubic Béziers."""
    pts = [sample(i, n, k / (KNOTS - 1)) for k in range(KNOTS)]

    def at(k: int) -> tuple[float, float]:
        return pts[max(0, min(len(pts) - 1, k))]

    out = [f"M{pts[0][0]:.0f},{pts[0][1]:.1f}"]
    for k in range(len(pts) - 1):
        p0, p1, p2, p3 = at(k - 1), at(k), at(k + 1), at(k + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(
            f"C{c1[0]:.0f},{c1[1]:.1f} {c2[0]:.0f},{c2[1]:.1f} {p2[0]:.0f},{p2[1]:.1f}"
        )
    return "".join(out)


def hero_field() -> str:
    paths = []
    for i in range(STROKES):
        d = stroke_path(i, STROKES)
        # Opacity rises with disorder so the ordered edge stays quiet and the
        # drape carries the weight.
        paths.append(f'<path d="{d}" style="--i:{i}" />')

    return (
        f'<svg class="linefield" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid slice" role="presentation" focusable="false" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'  <g class="linefield__strokes" fill="none" stroke="currentColor" '
        f'stroke-width="1" vector-effect="non-scaling-stroke">\n    '
        + "\n    ".join(paths)
        + "\n  </g>\n</svg>\n"
    )


def register(kind: str) -> str:
    """The four-stroke lane motif: straight for technical, bowed for art."""
    w, h, n = 64, 40, 4
    paths = []
    for i in range(n):
        y = h * (i + 0.5) / n
        if kind == "tech":
            d = f"M2,{y:.1f}L{w - 2},{y:.1f}"
        else:
            bow = 7 * math.sin((i + 1) / (n + 1) * math.pi)
            # Uneven pitch: the outer strokes sit closer, as in a fold.
            y += (i - (n - 1) / 2) * 1.8
            d = (
                f"M2,{y:.1f}"
                f"C{w * 0.3:.1f},{y - bow:.1f} {w * 0.7:.1f},{y + bow:.1f} {w - 2},{y:.1f}"
            )
        paths.append(f'<path d="{d}" />')

    return (
        f'<svg class="register register--{kind}" viewBox="0 0 {w} {h}" '
        f'role="presentation" focusable="false" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <g fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round">\n    '
        + "\n    ".join(paths)
        + "\n  </g>\n</svg>\n"
    )


def masthead_rule() -> str:
    """Six strokes tightening left to right — the mark, in miniature."""
    w, h, n = 34, 14, 6
    paths = []
    for i in range(n):
        # Pitch tightens toward the right edge.
        x = w * (i / (n - 1)) ** 1.6
        paths.append(f'<path d="M{x + 1:.1f},1L{x + 1:.1f},{h - 1}" />')
    return (
        f'<svg class="rule" viewBox="0 0 {w} {h}" role="presentation" '
        f'focusable="false" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <g fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round">\n    '
        + "\n    ".join(paths)
        + "\n  </g>\n</svg>\n"
    )


def main() -> int:
    PARTIALS.mkdir(parents=True, exist_ok=True)
    outputs = {
        "_linefield_home.svg": hero_field(),
        "_register_tech.svg": register("tech"),
        "_register_art.svg": register("art"),
        "_rule.svg": masthead_rule(),
    }
    for name, svg in outputs.items():
        path = PARTIALS / name
        path.write_text(svg, encoding="utf-8")
        print(f"  {name:26} {len(svg) / 1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
