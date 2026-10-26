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
from scripts.theme import ROOT

FIXTURES = ROOT / "tests" / "fixtures"
PAYLOAD = json.loads((FIXTURES / "graphql.json").read_text())
RSS = (FIXTURES / "rss.xml").read_text()


def fake_repos(slugs, token):
    # Look each slug up by name, so any order or subset of projects.json works.
    every = parse_repos(PAYLOAD, [f"r{i}" for i in range(len(PAYLOAD["data"]))])
    by_slug = {f"{r.owner}/{r.name}": r for r in every}
    return [by_slug[s] for s in slugs]


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        shutil.copytree(ROOT / "assets", self.tmp / "assets")
        for name in ("README.md", "projects.json"):
            shutil.copy(ROOT / name, self.tmp / name)
        for patch in (mock.patch.object(build, "ROOT", self.tmp),
                      mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}),
                      mock.patch.object(build, "fetch_repos", side_effect=fake_repos),
                      mock.patch.object(build, "fetch_feed", return_value=RSS)):
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
        self.assertEqual(len(paths), 2 * 18)  # header, 5 icons, follow, 3 labels, 7 cards, footer
        for path in paths:
            self.assertTrue((self.tmp / path).is_file(), path)

    def test_readme_blocks_filled(self):
        self.assertEqual(self.run_quietly("refresh"), 0)
        readme = (self.tmp / "README.md").read_text()
        self.assertIn('<a href="https://github.com/Sentrello/Sentrello"><picture>', readme)
        self.assertIn('srcset="assets/label-self-hosted-business-software-dark.svg"', readme)
        self.assertIn('alt="Self-hosted business software"', readme)
        self.assertIn("Read the rest on jamesconway.dev", readme)

    def test_featured_sits_above_the_pillars(self):
        self.assertEqual(self.run_quietly("refresh"), 0)
        readme = (self.tmp / "README.md").read_text()
        featured = readme.index('srcset="assets/card-conn3xorg-conn3x-featured-dark.svg"')
        self.assertLess(featured, readme.index("## My Top Open Source Projects"))
        self.assertIn('width="804"', readme[featured:readme.index("<!-- FEATURED:END -->")])
        self.assertNotIn("label-featured-project", readme)
        pillars = [readme.index(f"label-{p}-dark") for p in
                   ("high-performance-developer-tools", "linux-infrastructure", "self-hosted-business-software")]
        self.assertEqual(pillars, sorted(pillars))

    def test_trimmed_projects_drop_stale_assets(self):
        projects = json.loads((self.tmp / "projects.json").read_text())
        (self.tmp / "projects.json").write_text(json.dumps(projects[-1:]))
        self.assertEqual(self.run_quietly("refresh"), 0)
        assets = self.tmp / "assets"
        names = sorted(p.name for p in [*assets.glob("card-*.svg"), *assets.glob("label-*.svg")])
        self.assertEqual(names, [
            "card-sentrello-sentrello-dark.svg", "card-sentrello-sentrello-light.svg",
            "card-ticketslinger-ticketslinger-dark.svg", "card-ticketslinger-ticketslinger-light.svg",
            "label-self-hosted-business-software-dark.svg", "label-self-hosted-business-software-light.svg",
        ])
        self.assertTrue((self.tmp / "assets" / "header-dark.svg").is_file())
        self.assertNotIn("netweir", (self.tmp / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
