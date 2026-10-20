"""Project cards for the pinned repos, drawn from live GitHub data."""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from xml.sax.saxutils import escape

from scripts.chrome import STAR_PATH
from scripts.fonts import FAMILY, font_face_css, has_glyph, text_width
from scripts.theme import THEMES

API = "https://api.github.com/graphql"
FIELDS = "owner { login } name description url stargazerCount forkCount primaryLanguage { name color }"

WIDTH, HEIGHT = 400, 140
PAD = 20
TEXT_W = WIDTH - 2 * PAD
DESC, DESC_LINES = 13.5, 2
ICON = 12      # star and fork
SWATCH = 10
ITEM_GAP = 16  # between meta items
NAME_SIZE, NAME_SPACING = 20, -0.4

# Baselines, top to bottom. The meta row is pinned to the foot so it lines up
# across a row of cards whatever the description length.
Y_OWNER, Y_NAME, Y_DESC, DESC_LEAD, Y_META = 30, 54, 77, 18, 122

# Octicons repo-forked-16 (MIT), drawn on a 16px grid.
FORK_PATH = "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"


@dataclass
class Repo:
    owner: str
    name: str
    description: str
    language: str | None
    language_color: str | None
    stars: int
    forks: int
    url: str


def build_query(slugs: list[str]) -> str:
    parts = []
    for i, slug in enumerate(slugs):
        owner, name = slug.split("/")
        parts.append(f"r{i}: repository(owner: {json.dumps(owner)}, name: {json.dumps(name)}) {{ {FIELDS} }}")
    return "query { " + " ".join(parts) + " }"


def parse_repos(payload: dict, slugs: list[str]) -> list[Repo]:
    data = payload.get("data") or {}
    repos = []
    for i, slug in enumerate(slugs):
        node = data.get(f"r{i}")
        if node is None:
            raise RuntimeError(f"GitHub returned no repository for {slug}")
        lang = node["primaryLanguage"] or {}
        repos.append(Repo(
            owner=node["owner"]["login"], name=node["name"], description=node["description"] or "",
            language=lang.get("name"), language_color=lang.get("color"),
            stars=node["stargazerCount"], forks=node["forkCount"], url=node["url"],
        ))
    return repos


def fetch_repos(slugs: list[str], token: str) -> list[Repo]:
    req = urllib.request.Request(
        API, data=json.dumps({"query": build_query(slugs)}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "jamesconwaydev-readme",
                 "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub GraphQL request failed: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"GitHub GraphQL request failed: {getattr(e, 'reason', e)}") from e
    # GraphQL reports rate limits, bad scopes and unknown repos with a 200 and an errors list.
    if payload.get("errors"):
        raise RuntimeError("GitHub GraphQL errors: " + "; ".join(e.get("message", "?") for e in payload["errors"]))
    return parse_repos(payload, slugs)


def card_filename(repo: Repo, theme: str) -> str:
    return f"card-{repo.owner}-{repo.name}-{theme}.svg".lower()


def _clean(text: str, font: str) -> str:
    """Drop what the font can't draw (emoji, mostly) so nothing falls back to a system font."""
    return " ".join("".join(c for c in text if c.isspace() or has_glyph(c, font)).split())


def _wrap(text: str) -> list[str]:
    def fits(line):
        return text_width(line, "sans-400", DESC) <= TEXT_W

    lines, words = [], text.split()
    while words and len(lines) < DESC_LINES:
        n = 1
        while n < len(words) and fits(" ".join(words[:n + 1])):
            n += 1
        lines.append(" ".join(words[:n]))
        words = words[n:]
    if words:  # more to say than room: clamp the last line at a word boundary
        last = lines[-1].split()
        while len(last) > 1 and not fits(" ".join(last) + "…"):
            last.pop()
        lines[-1] = " ".join(last).rstrip(",.;:-") + "…"
    return lines


def _clamp_name(name: str) -> str:
    def fits(text):
        return text_width(text, "sans-800", NAME_SIZE, NAME_SPACING) <= TEXT_W

    if fits(name):
        return name
    while name and not fits(name + "…"):
        name = name[:-1]
    return name.rstrip() + "…"


def card_svg(repo: Repo, theme: str) -> str:
    c = THEMES[theme]
    owner = _clean(repo.owner, "mono-500") + " /"
    name = _clamp_name(_clean(repo.name, "sans-800"))
    desc = _clean(repo.description, "sans-400")
    lines = _wrap(desc)

    meta, mono_text, x = [], owner, PAD
    icon_y = Y_META - 4 - ICON / 2  # centre on the mono x-height
    if repo.language:
        lang = _clean(repo.language, "mono-500")
        meta.append(f'<rect class="swatch" x="{x}" y="{Y_META - 4 - SWATCH / 2:g}" width="{SWATCH}" height="{SWATCH}" '
                    f'fill="{repo.language_color or c["muted"]}"/>')
        x += SWATCH + 6
        meta.append(f'<text x="{x:.2f}" y="{Y_META}" class="m" fill="{c["muted"]}">{escape(lang)}</text>')
        x += text_width(lang, "mono-500", 12) + ITEM_GAP
        mono_text += lang
    for count, path in ((repo.stars, STAR_PATH), (repo.forks, FORK_PATH)):
        if count > 0:
            meta.append(f'<path transform="translate({x:g} {icon_y:g}) scale({ICON / 16:g})" fill="{c["muted"]}" d="{path}"/>')
            x += ICON + 4
            meta.append(f'<text x="{x:.2f}" y="{Y_META}" class="m" fill="{c["muted"]}">{count}</text>')
            x += text_width(str(count), "mono-500", 12) + ITEM_GAP
            mono_text += str(count)

    desc_svg = "\n".join(
        f'<text x="{PAD}" y="{Y_DESC + i * DESC_LEAD}" class="d" fill="{c["muted"]}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    title = f"{repo.owner}/{repo.name}" + (f": {repo.description}" if repo.description else "")
    fonts = font_face_css({k: v for k, v in {
        "mono-500": mono_text, "sans-800": name, "sans-400": "".join(lines),
    }.items() if v})
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">
<title>{escape(title)}</title>
<style>
{fonts}
.m{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:12px}}
.n{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:{NAME_SIZE}px;letter-spacing:{NAME_SPACING}px}}
.d{{font-family:{FAMILY["sans-400"]};font-weight:400;font-size:{DESC}px}}
</style>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" fill="{c["panel"]}" stroke="{c["line"]}"/>
<text x="{PAD}" y="{Y_OWNER}" class="m" fill="{c["muted"]}">{escape(owner)}</text>
<text x="{PAD}" y="{Y_NAME}" class="n" fill="{c["ink"]}">{escape(name)}</text>
{desc_svg}
{"".join(meta)}
</svg>
"""
