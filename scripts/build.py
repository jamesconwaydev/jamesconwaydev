"""Rebuild the README's generated blocks and every SVG it points at.

    python -m scripts.build refresh   cards, pillar labels, README
    python -m scripts.build all       all of that, plus header, icons, buttons, footer

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
from scripts.chrome import button_svg, footer_svg, icon_svg, label_svg
from scripts.feed import fetch_feed, parse_feed, posts_markdown, replace_block
from scripts.header import header_svg
from scripts.theme import ROOT

THEMES = ("dark", "light")
GENERATED = ("card-*.svg", "label-*.svg")  # named after projects.json, so they can go stale


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


def cards_block(projects: list[dict], repos: dict) -> str:
    rows = []
    for group in projects:
        pillar = group["pillar"]
        lines = [picture(f"label-{slug(pillar)}", pillar[:1].upper() + pillar[1:]) + "<br>"]
        for s in group["repos"]:
            r = repos[s]
            alt = f"{r.owner}/{r.name}" + (f": {r.description}" if r.description else "")
            name = card_filename(r, "dark").removesuffix("-dark.svg")
            lines.append(f'<a href="{escape(r.url)}">{picture(name, alt, 400)}</a>')
        rows.append("<p>\n" + "\n".join(lines) + "\n</p>")
    return "\n\n".join(rows)


def render(mode: str) -> dict[str, str]:
    """Every file this run owns, keyed by path relative to the repo root."""
    projects = json.loads((ROOT / "projects.json").read_text())
    slugs = [s for group in projects for s in group["repos"]]
    repos = dict(zip(slugs, fetch_repos(slugs, github_token())))
    posts = parse_feed(fetch_feed())

    readme = (ROOT / "README.md").read_text()
    readme = replace_block(readme, cards_block(projects, repos), "CARDS")
    files = {"README.md": replace_block(readme, posts_markdown(posts), "BLOG")}

    for theme in THEMES:
        for repo in repos.values():
            files[f"assets/{card_filename(repo, theme)}"] = card_svg(repo, theme)
        for group in projects:
            files[f"assets/label-{slug(group['pillar'])}-{theme}.svg"] = label_svg(group["pillar"], theme)
        if mode == "all":
            files[f"assets/header-{theme}.svg"] = header_svg(theme)
            files[f"assets/footer-{theme}.svg"] = footer_svg(theme)
            files[f"assets/button-follow-{theme}.svg"] = button_svg("FOLLOW ON GITHUB", theme, True, "plus")
            files[f"assets/button-star-{theme}.svg"] = button_svg("STAR A PROJECT BELOW", theme, False, "star")
            for icon in ("web", "linkedin", "x"):
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
