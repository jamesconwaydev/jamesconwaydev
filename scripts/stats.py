"""Public GitHub totals: searches for the counts, shallow clones for lines of code."""
import json
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from xml.sax.saxutils import escape

from scripts.cards import graphql
from scripts.fonts import FAMILY, font_face_css
from scripts.theme import THEMES

LOGIN = "jamesconwaydev"
BATCH = 50
CLONE_TIMEOUT = 300

WIDTH, HEIGHT = 832, 128
TILE_GAP, TILE_Y, TILE_H = 8, 34, 90
NOTE = "public work · refreshed daily"

CONTRIBUTED_QUERY = """query($login: String!, $after: String) { user(login: $login) {
  repositoriesContributedTo(first: 100, after: $after, privacy: PUBLIC, includeUserRepositories: true,
    contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, PULL_REQUEST_REVIEW, REPOSITORY]) {
    pageInfo { hasNextPage endCursor } nodes { nameWithOwner } }
  repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER) { nodes { nameWithOwner } }
} }"""
REPO_FIELDS = ("nameWithOwner name url stargazerCount isPrivate isEmpty "
               "owner { __typename login avatarUrl(size: 128) ... on Organization { name } }")


@dataclass
class PublicRepo:
    slug: str
    name: str
    url: str
    stars: int
    empty: bool
    owner: str
    owner_is_org: bool
    owner_name: str
    avatar_url: str


@dataclass
class Stats:
    commits: int
    prs: int
    issues: int
    lines: int
    repos: list[PublicRepo]

    @property
    def stars(self) -> int:
        return sum(r.stars for r in self.repos)


def search_count(kind: str, query: str, token: str) -> int:
    url = f"https://api.github.com/search/{kind}?per_page=1&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"Authorization": f"bearer {token}", "User-Agent": "jamesconwaydev-readme",
                                               "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)["total_count"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub search failed: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"GitHub search failed: {getattr(e, 'reason', e)}") from e


def contributed_slugs(token: str) -> set[str]:
    slugs, after = set(), None
    while True:
        user = graphql(CONTRIBUTED_QUERY, token, {"login": LOGIN, "after": after})["data"]["user"]
        page = user["repositoriesContributedTo"]
        slugs |= {n["nameWithOwner"] for n in page["nodes"]}
        # shortcut: owned repos stop at the first 100, page them too past that
        slugs |= {n["nameWithOwner"] for n in user["repositories"]["nodes"]}
        if not page["pageInfo"]["hasNextPage"]:
            return slugs
        after = page["pageInfo"]["endCursor"]


def parse_public(data: dict) -> list[PublicRepo]:
    """Deleted repos come back null and private ones are never counted, so both drop out."""
    return [PublicRepo(
        slug=n["nameWithOwner"], name=n["name"], url=n["url"], stars=n["stargazerCount"], empty=n["isEmpty"],
        owner=n["owner"]["login"], owner_is_org=n["owner"]["__typename"] == "Organization",
        owner_name=n["owner"].get("name") or n["owner"]["login"], avatar_url=n["owner"]["avatarUrl"],
    ) for n in data.values() if n and not n["isPrivate"]]


def fetch_public(slugs: list[str], token: str) -> list[PublicRepo]:
    repos = []
    for start in range(0, len(slugs), BATCH):
        parts = []
        for i, slug in enumerate(slugs[start:start + BATCH]):
            owner, name = slug.split("/")
            parts.append(f"r{i}: repository(owner: {json.dumps(owner)}, name: {json.dumps(name)}) {{ {REPO_FIELDS} }}")
        repos += parse_public(graphql("query { " + " ".join(parts) + " }", token, ignore_missing=True)["data"])
    return sorted(repos, key=lambda r: r.slug.lower())


def parse_grep_counts(output: str) -> int:
    """`git grep -c` prints rev:path:count, and only for text files with a line in them."""
    return sum(int(line.rsplit(":", 1)[1]) for line in output.splitlines() if line)


def count_repo_lines(repo: PublicRepo) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--no-checkout", f"{repo.url}.git", tmp],
                       check=True, capture_output=True, timeout=CLONE_TIMEOUT)
        done = subprocess.run(["git", "-C", tmp, "grep", "-I", "-c", "", "HEAD"],
                              capture_output=True, text=True, errors="replace", timeout=CLONE_TIMEOUT)
        if done.returncode not in (0, 1):  # 1 means no text files at all
            raise RuntimeError(f"git grep failed in {repo.slug}: {done.stderr.strip()}")
        return parse_grep_counts(done.stdout)


def count_lines(repos: list[PublicRepo]) -> int:
    with ThreadPoolExecutor(8) as pool:
        return sum(pool.map(count_repo_lines, [r for r in repos if not r.empty]))


def fetch_stats(known: list[str], token: str) -> Stats:
    """`known` keeps repos GitHub's contributed-to list, which only looks back so far, has dropped."""
    repos = fetch_public(sorted(contributed_slugs(token) | set(known)), token)
    return Stats(
        commits=search_count("commits", f"author:{LOGIN} is:public", token),
        prs=search_count("issues", f"author:{LOGIN} is:pr is:public", token),
        issues=search_count("issues", f"author:{LOGIN} is:issue is:public", token),
        lines=count_lines(repos),
        repos=repos,
    )


def short(n: int) -> str:
    return f"{n / 1_000_000:.1f}M" if n >= 1_000_000 else f"{n:,}"


def stat_rows(s: Stats) -> list[tuple[str, str]]:
    return [
        ("COMMITS", short(s.commits)), ("PULL REQUESTS", short(s.prs)), ("ISSUES", short(s.issues)),
        ("REPOS CONTRIBUTED", short(len(s.repos))), ("LINES OF CODE", short(s.lines)), ("STARS", short(s.stars)),
    ]


def stats_alt(s: Stats) -> str:
    return "GitHub stats, public work only: " + ", ".join(f"{v} {k.lower()}" for k, v in stat_rows(s)) + "."


def stats_svg(s: Stats, theme: str) -> str:
    c = THEMES[theme]
    rows = stat_rows(s)
    heading = "▸ GITHUB STATS"
    tile_w = (WIDTH - TILE_GAP * (len(rows) - 1)) / len(rows)
    tiles = []
    for i, (label, value) in enumerate(rows):
        x = i * (tile_w + TILE_GAP)
        mid = x + tile_w / 2
        tiles.append(
            f'<g class="rise" style="animation-delay:{i * .12:.2f}s">'
            f'<rect x="{x + .5:.2f}" y="{TILE_Y + .5}" width="{tile_w - 1:.2f}" height="{TILE_H - 1}" fill="{c["panel"]}" stroke="{c["line"]}"/>'
            f'<rect x="{x:.2f}" y="{TILE_Y}" width="{tile_w:.2f}" height="3" fill="{c["green"]}"/>'
            f'<text x="{mid:.2f}" y="{TILE_Y + 48}" text-anchor="middle" class="v" fill="{c["ink"]}">{escape(value)}</text>'
            f'<text x="{mid:.2f}" y="{TILE_Y + 72}" text-anchor="middle" class="m" fill="{c["muted"]}">{escape(label)}</text></g>'
        )
    fonts = font_face_css({
        "sans-800": "".join(v for _, v in rows),
        "mono-500": "".join(k for k, _ in rows) + NOTE,
        "mono-600": heading,
    })
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">
<title>{escape(stats_alt(s))}</title>
<style>
{fonts}
.m{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:10.5px}}
.n{{font-family:{FAMILY["mono-500"]};font-weight:500;font-size:12px}}
.l{{font-family:{FAMILY["mono-600"]};font-weight:600;font-size:13px;letter-spacing:2px}}
.v{{font-family:{FAMILY["sans-800"]};font-weight:800;font-size:27px;letter-spacing:-.6px}}
.rise{{animation:rise .5s ease-out both}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
<text y="20" class="l" fill="{c["green"]}">{escape(heading)}</text>
<text x="{WIDTH}" y="20" text-anchor="end" class="n" fill="{c["muted"]}">{escape(NOTE)}</text>
{"".join(tiles)}
</svg>
"""
