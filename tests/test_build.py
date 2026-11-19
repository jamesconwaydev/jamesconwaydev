import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import build
from scripts.cards import parse_repos
from scripts.feature import OrgCounts
from scripts.stats import PublicRepo, Stats
from scripts.theme import ROOT

FIXTURES = ROOT / "tests" / "fixtures"
PAYLOAD = json.loads((FIXTURES / "graphql.json").read_text())
RSS = (FIXTURES / "rss.xml").read_text()


def fake_repos(slugs, token):
    # Look each slug up by name, so any order or subset of projects.json works.
    every = parse_repos(PAYLOAD, [f"r{i}" for i in range(len(PAYLOAD["data"]))])
    by_slug = {f"{r.owner}/{r.name}": r for r in every}
    return [by_slug[s] for s in slugs]


STATS = Stats(commits=10, prs=5, issues=3, lines=1_500_000, repos=[
    PublicRepo("conn3xorg/conn3x", "conn3x", "https://github.com/conn3xorg/conn3x", 6, False,
               "conn3xorg", True, "Conn3x", "https://example.test/a.png"),
    PublicRepo("jamesconwaydev/aegis-v2", "aegis-v2", "https://github.com/jamesconwaydev/aegis-v2", 0, False,
               "jamesconwaydev", False, "jamesconwaydev", "https://example.test/b.png"),
])


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        shutil.copytree(ROOT / "assets", self.tmp / "assets")
        for name in ("README.md", "projects.json", "contributed.json"):
            shutil.copy(ROOT / name, self.tmp / name)
        for patch in (mock.patch.object(build, "ROOT", self.tmp),
                      mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}),
                      mock.patch.object(build, "fetch_repos", side_effect=fake_repos),
                      mock.patch.object(build, "fetch_feed", return_value=RSS),
                      mock.patch.object(build, "fetch_stats", return_value=STATS),
                      mock.patch.object(build, "fetch_org_counts", return_value=OrgCounts(106, 101)),
                      mock.patch.object(build, "fetch_avatar", return_value="data:image/png;base64,AAAA")):
            patch.start()
            self.addCleanup(patch.stop)

    def run_quietly(self, *argv):
        with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            return build.main(list(argv))

    def test_failure_writes_nothing(self):
        before = snapshot(self.tmp)
        with mock.patch.object(build, "fetch_feed", side_effect=RuntimeError("Feed request failed: HTTP 503")):
            self.assertEqual(self.run_quietly("refresh"), 1)
        self.assertEqual(snapshot(self.tmp), before)

    def test_bad_feed_writes_nothing(self):
        before = snapshot(self.tmp)
        with mock.patch.object(build, "fetch_feed", return_value="<rss><channel>"):
            self.assertEqual(self.run_quietly("all"), 1)
        self.assertEqual(snapshot(self.tmp), before)

    def test_no_token_writes_nothing(self):
        before = snapshot(self.tmp)
        with mock.patch.dict(os.environ, {"GITHUB_TOKEN": ""}), \
                mock.patch.object(build.subprocess, "run", side_effect=FileNotFoundError("gh")):
            self.assertEqual(self.run_quietly("refresh"), 1)
        self.assertEqual(snapshot(self.tmp), before)

    def test_refresh_is_stable(self):
        self.assertEqual(self.run_quietly("refresh"), 0)
        first = snapshot(self.tmp)
        with mock.patch.object(Path, "write_bytes") as write:
            self.assertEqual(self.run_quietly("refresh"), 0)
        write.assert_not_called()
        self.assertEqual(snapshot(self.tmp), first)

    def test_every_asset_referenced_exists(self):
        self.assertEqual(self.run_quietly("all"), 0)
        readme = (self.tmp / "README.md").read_text()
        paths = re.findall(r'(?:src|srcset)="(assets/[^"]+)"', readme)
        self.assertEqual(len(paths), 2 * 10)  # header, 5 icons, feature, 2 tiles, footer
        for path in paths:
            self.assertTrue((self.tmp / path).is_file(), path)

    def test_readme_blocks_filled(self):
        self.assertEqual(self.run_quietly("refresh"), 0)
        readme = (self.tmp / "README.md").read_text()
        self.assertNotIn("assets/card-", readme)
        self.assertNotIn("github.com/Sentrello", readme)
        self.assertNotIn("assets/label-", readme)
        self.assertNotIn("assets/stats-", readme)
        self.assertIn('srcset="assets/repo-conn3xorg-dark.svg"', readme)
        self.assertNotIn("follow-", readme)
        self.assertIn("Read the rest on jamesconway.dev", readme)

    def test_featured_sits_above_the_repo_icons(self):
        self.assertEqual(self.run_quietly("refresh"), 0)
        readme = (self.tmp / "README.md").read_text()
        featured = readme.index('srcset="assets/feature-conn3x-dark.svg"')
        self.assertLess(featured, readme.index("## Projects I Build and Contribute To"))
        self.assertIn('width="832"', readme[featured:readme.index("<!-- FEATURED:END -->")])
        self.assertNotIn("label-featured-project", readme)

    def test_no_card_groups_drops_stale_cards(self):
        (self.tmp / "assets" / "card-netweir-netweir-dark.svg").write_text("<svg/>")
        with mock.patch.object(build, "fetch_repos") as fetch:
            self.assertEqual(self.run_quietly("refresh"), 0)
        fetch.assert_not_called()
        self.assertEqual(list((self.tmp / "assets").glob("card-*.svg")), [])
        self.assertTrue((self.tmp / "assets" / "header-dark.svg").is_file())
        self.assertNotIn("CARDS:START", (self.tmp / "README.md").read_text())

if __name__ == "__main__":
    unittest.main()
