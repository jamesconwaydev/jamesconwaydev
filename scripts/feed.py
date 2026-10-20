"""Latest blog posts, pulled from the site's RSS feed into the README."""
import datetime
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime

FEED_URL = "https://jamesconway.dev/rss.xml"
BLOG_URL = "https://jamesconway.dev/blog/"


@dataclass
class Post:
    title: str
    url: str
    date: datetime.date
    summary: str


def parse_feed(xml: str, limit: int = 3) -> list[Post]:
    items = ET.fromstring(xml).findall("./channel/item")
    if not items:
        raise ValueError("feed has no items")
    posts = []
    for item in items:
        text = lambda tag: (item.findtext(tag) or "").strip()
        posts.append((parsedate_to_datetime(text("pubDate")), Post(
            title=text("title"), url=text("link"),
            date=parsedate_to_datetime(text("pubDate")).date(), summary=text("description"),
        )))
    posts.sort(key=lambda p: p[0], reverse=True)
    return [p for _, p in posts[:limit]]


def fetch_feed(url: str = FEED_URL) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "jamesconwaydev-readme"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Feed request failed: HTTP {resp.status}")
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Feed request failed: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"Feed request failed: {getattr(e, 'reason', e)}") from e


def _md(text: str) -> str:
    return re.sub(r"([\\\[\]*_<>])", r"\\\1", text)  # one pass, so the backslashes we add stay single


def posts_markdown(posts: list[Post]) -> str:
    entries = [f"`{p.date.isoformat()}` · **[{_md(p.title)}]({p.url})**<br>{_md(p.summary)}" for p in posts]
    entries.append(f"[Read the rest on jamesconway.dev →]({BLOG_URL})")
    return "\n\n".join(entries)


def replace_block(readme: str, block: str, name: str = "BLOG") -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    i, j = readme.find(start), readme.find(end)
    if i < 0 or j < i:
        raise ValueError(f"README needs {start} followed by {end}")
    return f"{readme[:i + len(start)]}\n{block}\n{readme[j:]}"
