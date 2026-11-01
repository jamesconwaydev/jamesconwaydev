"""One tile per project: an org is one project however many repos it holds."""
import base64
import urllib.error
import urllib.request
from dataclasses import dataclass
from xml.sax.saxutils import escape

from scripts.fonts import FAMILY, font_face_css, text_width
from scripts.stats import LOGIN, PublicRepo
from scripts.theme import THEMES

WIDTH, HEIGHT = 160, 112
LOGO, LOGO_Y = 60, 14
LABEL_SIZE = 12
SKIP = {f"{LOGIN}/{LOGIN}", f"{LOGIN}/.github"}  # profile plumbing, not projects
# Yours first, in this order. Anything else follows by stars.
ORDER = ("conn3xorg", "netweir", "tachyon-cms", "aegis-v2", "sentry-v2",
         "Sentrello", "ticketslinger", "githard", "blueprints")


def _tile(defs: str, art: str, glow: str) -> str:
    return (f'<defs><radialGradient id="halo"><stop offset="0" stop-color="{glow}" stop-opacity=".32"/>'
            f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>{defs}</defs>'
            f'<rect width="64" height="64" fill="#07090d"/><circle cx="32" cy="32" r="30" fill="url(#halo)"/>{art}')


def _grad(a: str, b: str) -> str:
    return f'<linearGradient id="ink" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'


# Drawn on a 64px grid, on the same near-black ground as the Conn3x, Netweir and
# TachyonCMS logos. Everything here has no logo of its own on GitHub.
LOGOS = {
    "aegis-v2": _tile(_grad("#ffd27a", "#e8603c"),
        '<path d="M32 12 48 18V31C48 41 41.5 48 32 52 22.5 48 16 41 16 31V18Z" fill="none" stroke="url(#ink)" stroke-width="3.5" stroke-linejoin="round"/>'
        '<path d="M22 32H27.5L30.5 25 34.5 39 37.5 32H42" fill="none" stroke="#fff4dc" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
        "#e8603c"),
    "sentry-v2": _tile(_grad("#7ff0c4", "#10b981"),
        '<g fill="none" stroke="url(#ink)" stroke-linecap="round"><path d="M14.5 32A17.5 17.5 0 0 1 32 14.5" stroke-width="3.5"/>'
        '<path d="M22 32A10 10 0 0 1 32 22" stroke-width="3.5" opacity=".75"/>'
        '<path d="M49.5 32A17.5 17.5 0 0 1 32 49.5" stroke-width="3.5" opacity=".5"/></g>'
        '<path d="M32 32 46 18" stroke="#dffbef" stroke-width="2.5" stroke-linecap="round"/><circle cx="32" cy="32" r="4" fill="#dffbef"/>',
        "#10b981"),
    "githard": _tile(_grad("#ffb56b", "#e8603c"),
        '<path d="M23 15V49M23 34C23 26 41 30 41 19" fill="none" stroke="url(#ink)" stroke-width="3.5" stroke-linecap="round"/>'
        '<circle cx="23" cy="49" r="4" fill="#ffb56b"/><circle cx="23" cy="15" r="4" fill="#ffb56b"/>'
        '<path d="M41 11 47.5 17.5 41 24 34.5 17.5Z" fill="#fff0e0"/>',
        "#e8913f"),
    "blueprints": _tile(_grad("#a8d4ff", "#3b82f6"),
        '<g stroke="#3b82f6" stroke-width=".8" opacity=".5"><path d="M15 26H49M15 38H49M26 15V49M38 15V49"/></g>'
        '<rect x="15" y="15" width="34" height="34" fill="none" stroke="url(#ink)" stroke-width="3"/>'
        '<path d="M15 49 38 26" stroke="#e4f2ff" stroke-width="2.5" stroke-linecap="round"/><circle cx="38" cy="26" r="3.5" fill="#e4f2ff"/>',
        "#3b82f6"),
    "ticketslinger": _tile(_grad("#7df0dc", "#14b8a6"),
        '<path d="M12 21H52V28A4 4 0 0 0 52 36V43H12V36A4 4 0 0 0 12 28Z" fill="none" stroke="url(#ink)" stroke-width="3.5" stroke-linejoin="round"/>'
        '<path d="M26 22V26M26 30V34M26 38V42" stroke="#7df0dc" stroke-width="2.5" stroke-linecap="round"/>'
        '<path d="M33 37 44 27" stroke="#e2fbf6" stroke-width="3" stroke-linecap="round"/>',
        "#14b8a6"),
    "simple-site": _tile(_grad("#f9a8d4", "#db2777"),
        '<rect x="13" y="16" width="38" height="32" rx="1" fill="none" stroke="url(#ink)" stroke-width="3.5"/>'
        '<path d="M13 25H51" stroke="url(#ink)" stroke-width="3"/><circle cx="19" cy="20.5" r="1.5" fill="#fde4f1"/><circle cx="25" cy="20.5" r="1.5" fill="#fde4f1"/>'
        '<path d="M20 33H36M20 40H30" stroke="#fde4f1" stroke-width="2.5" stroke-linecap="round"/>',
        "#db2777"),
}


@dataclass
class Project:
    key: str
    label: str
    url: str
    stars: int
    avatar_url: str | None


def projects_from(repos: list[PublicRepo]) -> list[Project]:
    found: dict[str, Project] = {}
    for r in repos:
        if r.slug in SKIP:
            continue
        if r.owner_is_org:
            p = found.setdefault(r.owner, Project(r.owner, r.owner_name, f"https://github.com/{r.owner}", 0, r.avatar_url))
            p.stars += r.stars
        else:  # a personal account isn't a project, so its repos stand alone
            found[r.name] = Project(r.name, r.name, r.url, r.stars, None if r.owner == LOGIN else r.avatar_url)

    def rank(p: Project):
        pinned = ORDER.index(p.key) if p.key in ORDER else len(ORDER)
        return pinned, -p.stars, p.key.lower()
    return sorted(found.values(), key=rank)


def fetch_avatar(url: str) -> str:
    """The owner's logo as a data URI: GitHub serves READMEs' SVGs with nothing external allowed."""
    req = urllib.request.Request(url, headers={"User-Agent": "jamesconwaydev-readme"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            kind = resp.headers.get_content_type()
            return f"data:{kind};base64,{base64.b64encode(resp.read()).decode()}"
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Avatar request failed: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"Avatar request failed: {getattr(e, 'reason', e)}") from e


def needs_avatar(p: Project) -> bool:
    return p.key not in LOGOS and p.avatar_url is not None


def tile_filename(p: Project, theme: str) -> str:
    return f"repo-{p.key}-{theme}.svg".lower()


def _clamp(label: str) -> str:
    while text_width(label, "mono-500", LABEL_SIZE) > WIDTH - 16:
        label = label[:-2] + "…"
    return label


def tile_svg(p: Project, theme: str, avatar: str | None = None) -> str:
    c = THEMES[theme]
    label = _clamp(p.label)
    x = (WIDTH - LOGO) / 2
    used = label
    if p.key in LOGOS:
        logo = f'<svg x="{x:g}" y="{LOGO_Y}" width="{LOGO}" height="{LOGO}" viewBox="0 0 64 64">{LOGOS[p.key]}</svg>'
        extra = ""
    elif avatar:
        logo = f'<image x="{x:g}" y="{LOGO_Y}" width="{LOGO}" height="{LOGO}" href="{avatar}"/>'
        extra = ""
    else:  # a new personal repo, until it gets a drawn logo
        logo = (f'<rect x="{x:g}" y="{LOGO_Y}" width="{LOGO}" height="{LOGO}" fill="#07090d" stroke="{c["green"]}"/>'
                f'<text x="{WIDTH / 2:g}" y="{LOGO_Y + 41}" text-anchor="middle" class="g" fill="{c["green"]}">{escape(p.key[0].upper())}</text>')
        extra = p.key[0].upper()
    fonts = font_face_css({k: v for k, v in {"mono-500": used, "sans-800": extra}.items() if v})
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">
<title>{escape(p.label)}</title>
<style>
{fonts}
.m{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:{LABEL_SIZE}px}}
.g{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:32px}}
</style>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" fill="{c["panel"]}" stroke="{c["line"]}"/>
{logo}
<text x="{WIDTH / 2:g}" y="97" text-anchor="middle" class="m" fill="{c["ink"]}">{escape(label)}</text>
</svg>
"""
