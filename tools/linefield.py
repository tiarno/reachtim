"""Generate the small masthead mark.

Six strokes with the pitch tightening left to right. That is the whole of the
site's ornament — it sits beside the wordmark and nowhere else.

    .venv/Scripts/python tools/linefield.py
"""

from __future__ import annotations

from pathlib import Path

PARTIALS = Path(__file__).resolve().parent.parent / "templates" / "partials"

W, H, N = 34, 14, 6


def masthead_rule() -> str:
    strokes = []
    for i in range(N):
        x = W * (i / (N - 1)) ** 1.6 + 1
        strokes.append(f'    <path d="M{x:.1f},1L{x:.1f},{H - 1}"/>')
    body = "\n".join(strokes)
    return (
        f'<svg class="rule" viewBox="0 0 {W} {H}" role="presentation" '
        f'focusable="false" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <g fill="none" stroke="currentColor" stroke-width="1.25" '
        f'stroke-linecap="round">\n'
        f"{body}\n"
        f"  </g>\n</svg>\n"
    )


def main() -> int:
    PARTIALS.mkdir(parents=True, exist_ok=True)
    path = PARTIALS / "_rule.svg"
    svg = masthead_rule()
    path.write_text(svg, encoding="utf-8")
    print(f"  {path.name:16} {len(svg)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
