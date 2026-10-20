"""The animated terminal at the top of the profile README."""
from xml.sax.saxutils import escape

from scripts.fonts import FAMILY, font_face_css, text_width
from scripts.theme import THEMES

TITLE_BAR = "jamesconwaydev@github: ~"
COMMAND = "whoami"
HEADLINE = ("I build software that solves", "real problems.")
LINES = ("self-hosted business software", "high-performance developer tools", "linux infrastructure")

WIDTH = 900
INSET = 30     # page background around the panel
PAD = 60       # left edge of the terminal content
BAR = 40       # title bar height
MONO = 22
HEAD, HEAD_SPACING = 46, -1.2

# Baselines, top to bottom. Tuned by eye against the approved mockup.
Y_PROMPT = 120
Y_HEAD = (194, 248)
Y_LINES = (306, 342, 378)
Y_END = 422
HEIGHT = Y_END + 36 + INSET  # block cursor hangs ~7px below its baseline

def _fits(text, font, size, x, spacing=0):
    right = x + text_width(text, font, size, spacing)
    if right > WIDTH - PAD:  # keep the right margin equal to the left
        raise ValueError(f"{text!r} runs past the panel ({right:.0f}px)")


def header_svg(theme: str) -> str:
    c = THEMES[theme]
    char = text_width("$", "mono-500", MONO)
    cmd_x = PAD + 2 * char
    cmd_w = text_width(COMMAND, "mono-500", MONO)
    bullet_x = PAD + 2 * char

    for line in HEADLINE:
        _fits(line, "sans-800", HEAD, PAD, HEAD_SPACING)
    for line in LINES:
        _fits(line, "mono-500", MONO, bullet_x)
    _fits(TITLE_BAR, "mono-500", 20, WIDTH / 2 - text_width(TITLE_BAR, "mono-500", 20) / 2)

    fonts = font_face_css({
        "mono-500": TITLE_BAR + COMMAND + "".join(LINES) + "$▸█",
        "sans-800": "".join(HEADLINE),
    })
    title = f"{' '.join(HEADLINE)} {LINES[0].capitalize()}, {LINES[1]}, {LINES[2]}."
    bar_mid = INSET + BAR / 2
    panel_h = HEIGHT - 2 * INSET - 1

    bullets = "\n".join(
        f'<g class="rise" style="animation-delay:{delay}s">'
        f'<text x="{PAD}" y="{y}" class="m" fill="{c["green"]}">▸</text>'
        f'<text x="{bullet_x:.2f}" y="{y}" class="m" fill="{c["ink"]}">{escape(line)}</text></g>'
        for line, y, delay in zip(LINES, Y_LINES, (2.0, 2.35, 2.7))
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">
<title>{escape(title)}</title>
<style>
{fonts}
.m{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:{MONO}px}}
.t{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:20px}}
.h{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:{HEAD}px;letter-spacing:{HEAD_SPACING}px}}
.cover{{transform:translateX({cmd_w:.2f}px);animation:type .8s steps(6) .3s both}}
.rise{{animation:rise .5s ease-out both}}
.cursor{{animation:blink 1s steps(1) infinite}}
@keyframes type{{from{{transform:translateX(0)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" fill="{c["bg"]}"/>
<rect x="{INSET + .5}" y="{INSET + .5}" width="{WIDTH - 2 * INSET - 1}" height="{panel_h}" fill="{c["panel"]}" stroke="{c["line"]}"/>
<line x1="{INSET + 1}" y1="{INSET + BAR + .5}" x2="{WIDTH - INSET - 1}" y2="{INSET + BAR + .5}" stroke="{c["line"]}"/>
<rect x="{INSET + 20}" y="{bar_mid - 6}" width="12" height="12" fill="{c["orange"]}"/>
<rect x="{INSET + 40}" y="{bar_mid - 6}" width="12" height="12" fill="{c["line"]}"/>
<rect x="{INSET + 60}" y="{bar_mid - 6}" width="12" height="12" fill="{c["green"]}"/>
<text x="{WIDTH / 2}" y="{bar_mid + 7}" text-anchor="middle" class="t" fill="{c["muted"]}">{escape(TITLE_BAR)}</text>
<text x="{PAD}" y="{Y_PROMPT}" class="m" fill="{c["green"]}">$</text>
<text x="{cmd_x:.2f}" y="{Y_PROMPT}" class="m" fill="{c["ink"]}">{escape(COMMAND)}</text>
<rect class="cover" x="{cmd_x:.2f}" y="{Y_PROMPT - 22}" width="{cmd_w:.2f}" height="30" fill="{c["panel"]}"/>
<g class="rise" style="animation-delay:1.3s">
<text x="{PAD}" y="{Y_HEAD[0]}" class="h" fill="{c["ink"]}">{escape(HEADLINE[0])}</text>
<text x="{PAD}" y="{Y_HEAD[1]}" class="h" fill="{c["green"]}">{escape(HEADLINE[1])}</text>
</g>
{bullets}
<g class="rise" style="animation-delay:3.1s">
<text x="{PAD}" y="{Y_END}" class="m" fill="{c["green"]}">$</text>
<text x="{cmd_x:.2f}" y="{Y_END}" class="m cursor" fill="{c["ink"]}">█</text>
</g>
</svg>
"""
