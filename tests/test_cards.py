import json
import re
import io
import unittest
import urllib.error
from unittest import mock
import xml.etree.ElementTree as ET

from scripts.cards import FORK_PATH, Repo, card_filename, card_svg, fetch_repos, parse_repos
from scripts.chrome import STAR_PATH
from scripts.theme import ROOT
from tests.support import SVG_NS, assert_self_contained

SLUGS = [s for p in json.loads((ROOT / "projects.json").read_text()) for s in p["repos"]]
FIXTURE = json.loads((ROOT / "tests" / "fixtures" / "graphql.json").read_text())


def repo(**kw):
    base = dict(owner="Sentrello", name="Sentrello", description="Short one.", language="TypeScript",
                language_color="#3178c6", stars=0, forks=0, url="https://github.com/Sentrello/Sentrello")
    return Repo(**{**base, **kw})


def texts(svg, cls):
    root = ET.fromstring(svg)
    return [t for t in root.iter(f"{{{SVG_NS}}}text") if cls in t.get("class", "").split()]


class CardsTest(unittest.TestCase):
    def test_parse_fixture(self):
        repos = parse_repos(FIXTURE, SLUGS)
        self.assertEqual(len(repos), 6)
        self.assertEqual((repos[0].owner, repos[0].name), ("Sentrello", "Sentrello"))
        self.assertGreaterEqual(repos[0].stars, 11)

    def test_missing_repo_raises(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["data"]["r5"] = None
        with self.assertRaisesRegex(RuntimeError, "jamesconwaydev/sentry-v2"):
            parse_repos(payload, SLUGS)

    def test_fetch_sends_token_and_parses(self):
        body = io.BytesIO(json.dumps(FIXTURE).encode())
        with mock.patch("urllib.request.urlopen", return_value=body) as urlopen:
            repos = fetch_repos(SLUGS, "tok")
        req = urlopen.call_args[0][0]
        self.assertEqual(req.get_header("Authorization"), "bearer tok")
        self.assertTrue(req.get_header("User-agent"))
        self.assertIn('repository(owner: "netweir", name: "netweir")', json.loads(req.data)["query"])
        self.assertEqual(len(repos), 6)

    def test_fetch_http_error_raises(self):
        err = urllib.error.HTTPError("https://api.github.com/graphql", 401, "Unauthorized", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaisesRegex(RuntimeError, "401"):
                fetch_repos(SLUGS, "bad")

    def test_graphql_errors_raise(self):
        body = io.BytesIO(json.dumps({"data": None, "errors": [{"message": "API rate limit exceeded"}]}).encode())
        with mock.patch("urllib.request.urlopen", return_value=body):
            with self.assertRaisesRegex(RuntimeError, "API rate limit exceeded"):
                fetch_repos(SLUGS, "tok")

    def test_network_failure_raises(self):
        for err in (urllib.error.URLError("nodename nor servname provided"), TimeoutError("timed out")):
            with mock.patch("urllib.request.urlopen", side_effect=err):
                with self.assertRaisesRegex(RuntimeError, "nodename|timed out"):
                    fetch_repos(SLUGS, "tok")

    def test_ampersand_escaped(self):
        aegis = parse_repos(FIXTURE, SLUGS)[4]
        svg = card_svg(aegis, "dark")
        ET.fromstring(svg)
        self.assertIn("&amp;", svg)

    def test_long_description_clamped(self):
        svg = card_svg(repo(description=" ".join(["pressure"] * 37)[:300]), "dark")
        lines = texts(svg, "d")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].text.endswith("…"))
        self.assertNotIn(" …", lines[1].text)

    def test_zero_counts_hidden(self):
        svg = card_svg(repo(stars=0, forks=0), "dark")
        self.assertNotIn(STAR_PATH, svg)
        self.assertNotIn(FORK_PATH, svg)
        self.assertEqual([t.text for t in texts(svg, "m")], ["Sentrello /", "TypeScript"])

    def test_counts_shown(self):
        svg = card_svg(repo(stars=11, forks=3), "dark")
        self.assertIn(STAR_PATH, svg)
        self.assertIn(FORK_PATH, svg)
        self.assertEqual([t.text for t in texts(svg, "m")][-2:], ["11", "3"])

    def test_no_language(self):
        svg = card_svg(repo(language=None, language_color=None, stars=4), "dark")
        self.assertNotIn('class="swatch"', svg)
        self.assertRegex(svg, r'<path transform="translate\(20 ')

    def test_unsupported_characters_dropped(self):
        svg = card_svg(repo(description="🚀 fast"), "dark")
        self.assertEqual([t.text for t in texts(svg, "d")], ["fast"])

    def test_filename(self):
        self.assertEqual(card_filename(repo(), "dark"), "card-sentrello-sentrello-dark.svg")

    def test_real_cards(self):
        for r in parse_repos(FIXTURE, SLUGS):
            for theme in ("dark", "light"):
                svg = card_svg(r, theme)
                root = ET.fromstring(svg)
                self.assertEqual((root.get("width"), root.get("height")), ("400", "140"))
                self.assertNotIn("★", svg)
                self.assertNotIn("⑂", svg)
                assert_self_contained(self, svg)
                self.assertTrue(re.search(r"<title>[^<]+/[^<]+</title>", svg))


if __name__ == "__main__":
    unittest.main()
