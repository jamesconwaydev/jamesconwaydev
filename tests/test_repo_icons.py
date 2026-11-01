import unittest
import xml.etree.ElementTree as ET

from scripts.repo_icons import LOGOS, Project, needs_avatar, projects_from, tile_svg
from scripts.stats import LOGIN, PublicRepo
from tests.support import assert_self_contained


def repo(owner, name, stars=0, org=True):
    return PublicRepo(f"{owner}/{name}", name, f"https://github.com/{owner}/{name}", stars, False,
                      owner, org, owner.title(), "https://example.test/a.png")


class RepoIconsTest(unittest.TestCase):
    def test_an_org_is_one_project_with_all_its_stars(self):
        tiles = projects_from([repo("conn3xorg", "conn3x", 6), repo("conn3xorg", "circuit-k3s", 4)])
        self.assertEqual([(p.key, p.stars, p.url) for p in tiles], [("conn3xorg", 10, "https://github.com/conn3xorg")])

    def test_profile_plumbing_gets_no_tile(self):
        tiles = projects_from([repo(LOGIN, LOGIN, org=False), repo(LOGIN, ".github", org=False), repo(LOGIN, "aegis-v2", org=False)])
        self.assertEqual([p.key for p in tiles], ["aegis-v2"])

    def test_yours_first_then_by_stars(self):
        tiles = projects_from([repo("big", "x", 9000), repo("small", "y", 1), repo("netweir", "netweir", 6)])
        self.assertEqual([p.key for p in tiles], ["netweir", "big", "small"])

    def test_placeholder_avatars_are_replaced_by_drawn_logos(self):
        tiles = projects_from([repo("ticketslinger", "ticketslinger"), repo("mrpinkapps", "simple-site", org=False)])
        self.assertFalse(any(needs_avatar(p) for p in tiles))

    def test_every_kind_of_tile_is_self_contained(self):
        for p, avatar in ((Project("aegis-v2", "aegis-v2", "u", 0, None), None),
                          (Project("netweir", "Netweir", "u", 0, "a"), "data:image/png;base64,AAAA"),
                          (Project("brand-new", "brand-new", "u", 0, None), None)):
            svg = tile_svg(p, "dark", avatar)
            ET.fromstring(svg)
            assert_self_contained(self, svg)

    def test_logos_parse(self):
        for key in LOGOS:
            ET.fromstring(tile_svg(Project(key, key, "u", 0, None), "light"))


if __name__ == "__main__":
    unittest.main()
