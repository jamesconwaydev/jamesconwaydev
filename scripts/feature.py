"""The Conn3x feature: a chip bridging IaC and configuration management, with live counts."""
import math
from dataclasses import dataclass
from xml.sax.saxutils import escape

from scripts.cards import graphql
from scripts.fonts import FAMILY, font_face_css
from scripts.theme import THEMES

ORG = "conn3xorg"
URL = f"https://github.com/{ORG}/conn3x"
WIDTH = 832
HEADLINE = "The gap was never supposed to be there."
SUB = "Creating a server and setting it up are one job. Now it's one tool."
LEFT_HEAD, RIGHT_HEAD = "INFRASTRUCTURE AS CODE", "CONFIGURATION MANAGEMENT"
LEFT, RIGHT = ("AWS", "Hetzner", "Proxmox"), ("nginx", "postgres", "k3s")
BAND = "EVERY LIGHT IS A CIRCUIT YOU DON'T HAVE TO WRITE"
CLOUDS = 10  # clouds and hypervisors on conn3x.org: GitHub has no way to count these

CHIP_X, CHIP_W, CHIP_Y, CHIP_H = 354, 124, 136, 96
ROW_Y = (130, 184, 238)
NODE_L, NODE_R = 112, 720  # where the traces meet the node labels
LED, PITCH, LED_COLS, Y_BAND = 6, 10, 78, 300

ORG_QUERY = """query($org: String!, $after: String) { organization(login: $org) {
  repositories(first: 100, after: $after, privacy: PUBLIC) { pageInfo { hasNextPage endCursor } nodes { name } }
} }"""


@dataclass
class OrgCounts:
    repos: int
    circuits: int


def fetch_org_counts(token: str) -> OrgCounts:
    names, after = [], None
    while True:
        page = graphql(ORG_QUERY, token, {"org": ORG, "after": after})["data"]["organization"]["repositories"]
        names += [n["name"] for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"]:
            return OrgCounts(len(names), sum(n.startswith("circuit-") for n in names))
        after = page["pageInfo"]["endCursor"]


def feature_alt(n: OrgCounts) -> str:
    return (f"Conn3x bridges infrastructure as code and configuration management: one binary, one plan, one state. "
            f"{CLOUDS} clouds and hypervisors, {n.circuits} circuits, {n.repos} repos in the org.")


def _trace(d: str, colour: str, delay: float) -> str:
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.2" opacity=".55"/>'
            f'<path class="pulse" pathLength="100" d="{d}" fill="none" stroke="{colour}" stroke-width="2.5" '
            f'stroke-linecap="square" style="animation-delay:{delay:.1f}s"/>')


def feature_svg(n: OrgCounts, theme: str) -> str:
    c = THEMES[theme]
    orange, green = c["orange"], c["green"]
    chip_r = CHIP_X + CHIP_W
    chip_mid = CHIP_Y + CHIP_H / 2

    traces = []
    for i, y in enumerate(ROW_Y):
        pin = chip_mid + (i - 1) * 26
        delay = i * .8
        traces.append(_trace(f"M{NODE_L} {y}H230L280 {pin:g}H{CHIP_X}", orange, delay))
        traces.append(_trace(f"M{chip_r} {pin:g}H552L602 {y}H{NODE_R}", green, delay + 1.2))
    left = "".join(f'<text x="{NODE_L - 10}" y="{y + 4}" text-anchor="end" class="m" fill="{orange}">{escape(t)}</text>'
                   for t, y in zip(LEFT, ROW_Y))
    right = "".join(f'<text x="{NODE_R + 10}" y="{y + 4}" class="m" fill="{green}">{escape(t)}</text>'
                    for t, y in zip(RIGHT, ROW_Y))
    pins = "".join(
        f'<rect x="{CHIP_X + 14 + i * 16}" y="{y}" width="8" height="6" fill="{c["line"]}"/>'
        for i in range(7) for y in (CHIP_Y - 6, CHIP_Y + CHIP_H)
    )

    # One light per circuit, so the band grows as circuits ship.
    rows = max(1, math.ceil(n.circuits / LED_COLS))
    y_leds = Y_BAND + 12
    x_leds = (WIDTH - (LED_COLS * PITCH - (PITCH - LED))) / 2
    leds = "".join(
        f'<rect class="led" x="{x_leds + (i % LED_COLS) * PITCH:g}" y="{y_leds + (i // LED_COLS) * PITCH}" '
        f'width="{LED}" height="{LED}" fill="{green}" style="animation-delay:{(i * 37 % 41) / 10:.1f}s"/>'
        for i in range(n.circuits)
    )
    y_rule = y_leds + rows * PITCH + 12
    y_value, y_label = y_rule + 38, y_rule + 58
    height = y_label + 22

    stats = [(f"{CLOUDS}", "CLOUDS AND HYPERVISORS"), ("1", "BINARY, NO AGENT, NO PYTHON"),
             (f"{n.circuits}", "CIRCUITS AND COUNTING"), (f"{n.repos}", "REPOS IN THE ORG")]
    cells = "".join(
        f'<text x="{WIDTH * (2 * i + 1) / 8:g}" y="{y_value}" text-anchor="middle" class="v" fill="{c["ink"]}">{escape(v)}</text>'
        f'<text x="{WIDTH * (2 * i + 1) / 8:g}" y="{y_label}" text-anchor="middle" class="s" fill="{c["muted"]}">{escape(k)}</text>'
        for i, (v, k) in enumerate(stats)
    )
    fonts = font_face_css({
        "sans-800": HEADLINE + "conn3x" + "".join(v for v, _ in stats),
        "sans-400": SUB,
        "mono-500": LEFT_HEAD + RIGHT_HEAD + BAND + "one plan" + "".join(LEFT + RIGHT) + "".join(k for _, k in stats),
    })
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img">
<title>{escape(feature_alt(n))}</title>
<defs>
<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{c["line"]}"/></pattern>
<radialGradient id="glow"><stop offset="0" stop-color="{green}" stop-opacity=".42"/><stop offset="1" stop-color="{green}" stop-opacity="0"/></radialGradient>
<linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{orange}"/><stop offset="1" stop-color="{green}"/></linearGradient>
</defs>
<style>
{fonts}
.h{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:31px;letter-spacing:-.7px}}
.b{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:23px}}
.v{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:25px}}
.d{{font-family:{FAMILY["sans-400"]};font-weight:400;font-size:14.5px}}
.m{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:12px}}
.s{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:10.5px}}
.pulse{{stroke-dasharray:14 200;stroke-dashoffset:14;animation:run 2.4s linear infinite}}
.glow{{transform-origin:416px {chip_mid:g}px;animation:breathe 2.4s ease-in-out infinite}}
.led{{opacity:.28;animation:twinkle 4.1s ease-in-out infinite}}
@keyframes run{{to{{stroke-dashoffset:-100}}}}
@keyframes breathe{{50%{{opacity:.45;transform:scale(.88)}}}}
@keyframes twinkle{{40%{{opacity:1}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.pulse{{opacity:0}}.led{{opacity:.8}}}}
</style>
<rect width="{WIDTH}" height="{height}" fill="{c["bg"]}"/>
<rect width="{WIDTH}" height="{height}" fill="url(#dots)" opacity=".55"/>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" fill="none" stroke="{c["line"]}"/>
<rect width="{WIDTH}" height="4" fill="url(#rule)"/>
<text x="416" y="50" text-anchor="middle" class="h" fill="{c["ink"]}">{escape(HEADLINE)}</text>
<text x="416" y="76" text-anchor="middle" class="d" fill="{c["muted"]}">{escape(SUB)}</text>
<text x="24" y="104" class="s" fill="{orange}">{LEFT_HEAD}</text>
<text x="{WIDTH - 24}" y="104" text-anchor="end" class="s" fill="{green}">{RIGHT_HEAD}</text>
{"".join(traces)}
{left}{right}
<circle class="glow" cx="416" cy="{chip_mid:g}" r="118" fill="url(#glow)"/>
{pins}
<rect x="{CHIP_X}" y="{CHIP_Y}" width="{CHIP_W}" height="{CHIP_H}" fill="{c["panel"]}" stroke="{green}" stroke-width="2"/>
<text x="416" y="{chip_mid + 2:g}" text-anchor="middle" class="b" fill="{c["ink"]}">conn3x</text>
<text x="416" y="{chip_mid + 24:g}" text-anchor="middle" class="m" fill="{c["muted"]}">one plan</text>
<text x="416" y="{Y_BAND}" text-anchor="middle" class="s" fill="{c["muted"]}">{escape(BAND)}</text>
{leds}
<line x1="24" y1="{y_rule}" x2="{WIDTH - 24}" y2="{y_rule}" stroke="{c["line"]}"/>
{cells}
</svg>
"""
