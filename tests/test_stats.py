import unittest
import xml.etree.ElementTree as ET

from scripts.stats import Stats, parse_grep_counts, parse_public, short, stats_svg
from tests.support import assert_self_contained


def node(slug, stars=1, private=False):
    owner, name = slug.split("/")
    return {"nameWithOwner": slug, "name": name, "url": f"https://github.com/{slug}", "stargazerCount": stars,
            "isPrivate": private, "isEmpty": False,
            "owner": {"__typename": "Organization", "login": owner, "avatarUrl": "https://example.test/a.png"}}


class StatsTest(unittest.TestCase):
    def test_grep_counts_survive_colons_in_paths(self):
        self.assertEqual(parse_grep_counts("HEAD:a.py:10\nHEAD:odd:name.txt:5\n"), 15)
        self.assertEqual(parse_grep_counts(""), 0)

    def test_deleted_and_private_repos_never_count(self):
        repos = parse_public({"r0": node("a/b", 4), "r1": None, "r2": node("a/secret", 9, private=True)})
        stats = Stats(1, 1, 1, 1, repos)
        self.assertEqual([r.slug for r in repos], ["a/b"])
        self.assertEqual(stats.stars, 4)

    def test_short(self):
        self.assertEqual(short(11737), "11,737")
        self.assertEqual(short(2_640_000), "2.6M")

    def test_svg(self):
        for theme in ("dark", "light"):
            svg = stats_svg(Stats(1891, 866, 298, 2_640_000, parse_public({"r0": node("a/b", 4)})), theme)
            ET.fromstring(svg)
            assert_self_contained(self, svg)
            for text in ("1,891", "PULL REQUESTS", "2.6M", "prefers-reduced-motion"):
                self.assertIn(text, svg)


if __name__ == "__main__":
    unittest.main()
