"""Social icons, call-to-action buttons, pillar labels and the rule at the foot of the README."""
from xml.sax.saxutils import escape

from scripts.fonts import FAMILY, font_face_css, text_width
from scripts.theme import THEMES

ICON = 48
GLYPH = 22

# Simple Icons (CC0), all drawn on a 24px grid.
GLYPHS = {
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z",
    "mastodon": "M23.268 5.313c-.35-2.578-2.617-4.61-5.304-5.004C17.51.242 15.792 0 11.813 0h-.03c-3.98 0-4.835.242-5.288.309C3.882.692 1.496 2.518.917 5.127.64 6.412.61 7.837.661 9.143c.074 1.874.088 3.745.26 5.611.118 1.24.325 2.47.62 3.68.55 2.237 2.777 4.098 4.96 4.857 2.336.792 4.849.923 7.256.38.265-.061.527-.132.786-.213.585-.184 1.27-.39 1.774-.753a.057.057 0 0 0 .023-.043v-1.809a.052.052 0 0 0-.02-.041.053.053 0 0 0-.046-.01 20.282 20.282 0 0 1-4.709.545c-2.73 0-3.463-1.284-3.674-1.818a5.593 5.593 0 0 1-.319-1.433.053.053 0 0 1 .066-.054c1.517.363 3.072.546 4.632.546.376 0 .75 0 1.125-.01 1.57-.044 3.224-.124 4.768-.422.038-.008.077-.015.11-.024 2.435-.464 4.753-1.92 4.989-5.604.008-.145.03-1.52.03-1.67.002-.512.167-3.63-.024-5.545zm-3.748 9.195h-2.561V8.29c0-1.309-.55-1.976-1.67-1.976-1.23 0-1.846.79-1.846 2.35v3.403h-2.546V8.663c0-1.56-.617-2.35-1.848-2.35-1.112 0-1.668.668-1.67 1.977v6.218H4.822V8.102c0-1.31.337-2.35 1.011-3.12.696-.77 1.608-1.164 2.74-1.164 1.311 0 2.302.5 2.962 1.498l.638 1.06.638-1.06c.66-.999 1.65-1.498 2.96-1.498 1.13 0 2.043.395 2.74 1.164.675.77 1.012 1.81 1.012 3.12z",
    "bluesky": "M5.202 2.857C7.954 4.922 10.913 9.11 12 11.358c1.087-2.247 4.046-6.436 6.798-8.501C20.783 1.366 24 .213 24 3.883c0 .732-.42 6.156-.667 7.037-.856 3.061-3.978 3.842-6.755 3.37 4.854.826 6.089 3.562 3.422 6.299-5.065 5.196-7.28-1.304-7.847-2.97-.104-.305-.152-.448-.153-.327 0-.121-.05.022-.153.327-.568 1.666-2.782 8.166-7.847 2.97-2.667-2.737-1.432-5.473 3.422-6.3-2.777.473-5.899-.308-6.755-3.369C.42 10.04 0 4.615 0 3.883c0-3.67 3.217-2.517 5.202-1.026",
    "x": "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z",
}
TITLES = {"web": "jamesconway.dev", "linkedin": "LinkedIn", "x": "X", "mastodon": "Mastodon", "bluesky": "Bluesky"}

BUTTON_H = 44
PAD = 20
MARK = 14      # plus and star share one square
GAP = 10       # between the mark and the label
SPACING = 1.4
# Octicons star-fill-16 (MIT), drawn on a 16px grid.
STAR_PATH = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"

FOOT_W, FOOT_H, SQUARE = 900, 40, 12

LABEL_H, LABEL_SIZE, LABEL_SPACING = 28, 13, 2


def icon_svg(name: str, theme: str) -> str:
    c = THEMES[theme]
    if name == "web":  # globe: circle plus two meridians and the equator
        glyph = (f'<g fill="none" stroke="{c["ink"]}" stroke-width="1.8">'
                 '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></g>')
    else:
        glyph = f'<path fill="{c["ink"]}" d="{GLYPHS[name]}"/>'
    off = (ICON - GLYPH) / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ICON}" height="{ICON}" viewBox="0 0 {ICON} {ICON}" role="img">
<title>{escape(TITLES[name])}</title>
<rect x=".5" y=".5" width="{ICON - 1}" height="{ICON - 1}" fill="{c["bg"]}" stroke="{c["line"]}"/>
<g transform="translate({off} {off}) scale({GLYPH / 24:.5f})">{glyph}</g>
</svg>
"""


def button_svg(label: str, theme: str, solid: bool, icon: str | None = None) -> str:
    c = THEMES[theme]
    ink = "#0d1117" if solid else c["ink"]
    fill, stroke = (c["green"], c["green"]) if solid else (c["bg"], c["line"])
    title = {"plus": "Follow James Conway on GitHub", "star": "Star a project below"}.get(icon, label)
    text_w = text_width(label, "mono-600", 14, SPACING)
    lead = MARK + GAP if icon else 0
    width = round(PAD + lead + text_w + PAD, 2)
    y = BUTTON_H / 2 - MARK / 2

    if icon == "plus":  # two square-ended bars
        mark = (f'<rect x="{PAD}" y="{BUTTON_H / 2 - 1}" width="{MARK}" height="2" fill="{ink}"/>'
                f'<rect x="{PAD + MARK / 2 - 1}" y="{y}" width="2" height="{MARK}" fill="{ink}"/>')
    elif icon == "star":
        mark = f'<path transform="translate({PAD} {y}) scale({MARK / 16})" fill="{ink}" d="{STAR_PATH}"/>'
    else:
        mark = ""

    fonts = font_face_css({"mono-600": label})
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{BUTTON_H}" viewBox="0 0 {width:g} {BUTTON_H}" role="img">
<title>{escape(title)}</title>
<style>
{fonts}
.b{{font-family:{FAMILY["mono-600"]};font-weight:600;font-size:14px;letter-spacing:{SPACING}px}}
</style>
<rect x=".5" y=".5" width="{width - 1:g}" height="{BUTTON_H - 1}" fill="{fill}" stroke="{stroke}"/>
{mark}
<text x="{PAD + lead}" y="27" class="b" fill="{ink}">{escape(label)}</text>
</svg>
"""


def footer_svg(theme: str) -> str:
    c = THEMES[theme]
    mid = FOOT_H / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{FOOT_W}" height="{FOOT_H}" viewBox="0 0 {FOOT_W} {FOOT_H}" role="img">
<title>End of profile</title>
<rect y="{mid:g}" width="{FOOT_W}" height="1" fill="{c["line"]}"/>
<rect x="{(FOOT_W - SQUARE) / 2:g}" y="{mid - SQUARE / 2:g}" width="{SQUARE}" height="{SQUARE}" fill="{c["green"]}"/>
</svg>
"""


def label_svg(text: str, theme: str) -> str:
    """The small green heading over each row of project cards."""
    shown = f"▸ {text.upper()}"
    width = round(text_width(shown, "mono-600", LABEL_SIZE, LABEL_SPACING) + 1, 2)
    fonts = font_face_css({"mono-600": shown})
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{LABEL_H}" viewBox="0 0 {width:g} {LABEL_H}" role="img">
<title>{escape(text[:1].upper() + text[1:])}</title>
<style>
{fonts}
.l{{font-family:{FAMILY["mono-600"]};font-weight:600;font-size:{LABEL_SIZE}px;letter-spacing:{LABEL_SPACING}px}}
</style>
<text y="20" class="l" fill="{THEMES[theme]["green"]}">{escape(shown)}</text>
</svg>
"""
