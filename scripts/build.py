"""Rebuild the README's generated blocks and every SVG it points at.

    python -m scripts.build refresh   feature, cards, repo icons, README
    python -m scripts.build all       all of that, plus header, social icons, footer

Everything is fetched and rendered in memory first, so a failed request
leaves the repo exactly as it was.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from html import escape

from scripts.cards import card_filename, card_svg, fetch_repos
from scripts.chrome import footer_svg, icon_svg
from scripts.feature import URL as FEATURE_URL, feature_alt, feature_svg, fetch_org_counts
from scripts.feed import fetch_feed, parse_feed, posts_markdown, replace_block
from scripts.header import header_svg
from scripts.repo_icons import fetch_avatar, needs_avatar, projects_from, tile_filename, tile_svg
from scripts.stats import fetch_stats
from scripts.theme import ROOT

THEMES = ("dark", "light")
GENERATED = ("card-*.svg", "label-*.svg", "repo-*.svg")  # named after live data, so they can go stale
FULL_WIDTH = 832  # two cards and the gap between them
CARD_GAP = "&emsp;&emsp;"
FEATURE_LINKS = (("Website", "https://conn3x.org"), ("Docs", "https://docs.conn3x.org/get-started"),
                 ("Circuits", "https://conn3x.org/circuits"), ("GitHub", FEATURE_URL),
                 ("YouTube", "https://www.youtube.com/@conn3xlabs"))


def github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    if not token:
        raise RuntimeError("no GitHub token: set GITHUB_TOKEN or run gh auth login")
    return token


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def picture(name: str, alt: str, width: int | None = None) -> str:
    """A themed image: GitHub swaps in the dark file when the viewer is on a dark theme."""
    size = f' width="{width}"' if width else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
            f'<img src="assets/{name}-light.svg" alt="{escape(alt)}"{size}></picture>')


def card_link(r) -> str:
    alt = f"{r.owner}/{r.name}" + (f": {r.description}" if r.description else "")
    name = card_filename(r, "dark").removesuffix("-dark.svg")
    return f'<a href="{escape(r.url)}">{picture(name, alt, 400)}</a>'


def featured_block(counts) -> str:
    links = " · ".join(f'<a href="{url}">{text}</a>' for text, url in FEATURE_LINKS)
    return (f'<p>\n<a href="{FEATURE_URL}">{picture("feature-conn3x", feature_alt(counts), FULL_WIDTH)}</a>\n</p>\n\n'
            f'<p align="center">\n<code>brew install conn3xorg/tap/conn3x</code><br>\n{links}\n</p>')


def cards_block(projects: list[dict], repos: dict) -> str:
    rows = []
    for group in (g for g in projects if not g.get("featured")):
        cards = CARD_GAP.join(card_link(repos[s]) for s in group["repos"])
        rows.append(f"<p>\n{cards}\n</p>")
    return "\n\n<br>\n\n".join(rows)


def icons_block(tiles) -> str:
    links = [f'<a href="{escape(p.url)}">{picture(tile_filename(p, "dark").removesuffix("-dark.svg"), p.label, 132)}</a>'
             for p in tiles]
    return '<p align="center">\n' + "\n".join(links) + "\n</p>"


def render(mode: str) -> dict[str, str]:
    """Every file this run owns, keyed by path relative to the repo root."""
    projects = json.loads((ROOT / "projects.json").read_text())
    known = json.loads((ROOT / "contributed.json").read_text())
    token = github_token()
    slugs = [s for group in projects if not group.get("featured") for s in group["repos"]]
    repos = dict(zip(slugs, fetch_repos(slugs, token)))
    posts = parse_feed(fetch_feed())
    stats = fetch_stats(known, token)
    counts = fetch_org_counts(token)
    tiles = projects_from(stats.repos)
    avatars = {p.key: fetch_avatar(p.avatar_url) for p in tiles if needs_avatar(p)}

    readme = (ROOT / "README.md").read_text()
    readme = replace_block(readme, featured_block(counts), "FEATURED")
    readme = replace_block(readme, cards_block(projects, repos), "CARDS")
    readme = replace_block(readme, icons_block(tiles), "REPOS")
    files = {
        "README.md": replace_block(readme, posts_markdown(posts), "BLOG"),
        "contributed.json": json.dumps(sorted(r.slug for r in stats.repos), indent=0) + "\n",
    }

    for theme in THEMES:
        files[f"assets/feature-conn3x-{theme}.svg"] = feature_svg(counts, theme)
        for p in tiles:
            files[f"assets/{tile_filename(p, theme)}"] = tile_svg(p, theme, avatars.get(p.key))
        for group in projects:
            if group.get("featured"):
                continue
            for s in group["repos"]:
                files[f"assets/{card_filename(repos[s], theme)}"] = card_svg(repos[s], theme)
        if mode == "all":
            files[f"assets/header-{theme}.svg"] = header_svg(theme)
            files[f"assets/footer-{theme}.svg"] = footer_svg(theme)
            for icon in ("web", "linkedin", "x", "mastodon", "bluesky"):
                files[f"assets/icon-{icon}-{theme}.svg"] = icon_svg(icon, theme)
    return files


def write(files: dict[str, str]) -> None:
    for rel, text in files.items():
        path, data = ROOT / rel, text.encode()
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
            print(f"wrote {rel}")
    for pattern in GENERATED:
        for path in (ROOT / "assets").glob(pattern):
            if f"assets/{path.name}" not in files:
                path.unlink()
                print(f"removed assets/{path.name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.build", description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("all", "refresh"))
    mode = parser.parse_args(argv).mode
    try:
        files = render(mode)
    except Exception as e:  # anything at all: bad token, network, malformed feed
        print(f"build failed: {e}", file=sys.stderr)
        return 1
    write(files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
