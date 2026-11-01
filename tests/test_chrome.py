import unittest
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from scripts.chrome import footer_svg, icon_svg, label_svg
from tests.support import assert_self_contained

THEMES = ("dark", "light")


def width(svg):
    return float(ET.fromstring(svg).get("width"))


class ChromeTest(unittest.TestCase):
    def test_icons_parse_both_themes(self):
        for theme in THEMES:
            for name in ("web", "linkedin", "x", "mastodon", "bluesky"):
                root = ET.fromstring(icon_svg(name, theme))
                self.assertEqual((root.get("width"), root.get("height")), ("48", "48"))

    def test_footer_has_green_square(self):
        for theme in THEMES:
            svg = footer_svg(theme)
            ET.fromstring(svg)
            self.assertIn("#10b981", svg)

    def test_label_is_green_uppercase_mono(self):
        for theme in THEMES:
            svg = label_svg("linux infrastructure", theme)
            root = ET.fromstring(svg)
            self.assertEqual(root.get("height"), "28")
            self.assertIn(">▸ LINUX INFRASTRUCTURE</text>", svg)
            self.assertIn('fill="#10b981"', svg)
            self.assertIn("<title>Linux infrastructure</title>", svg)

    def test_label_width_tracks_text(self):
        self.assertGreater(width(label_svg("high-performance developer tools", "dark")),
                           width(label_svg("linux", "dark")))

    def test_no_external_refs(self):
        for theme in THEMES:
            for svg in (icon_svg("x", theme), footer_svg(theme),
                        label_svg("linux infrastructure", theme)):
                assert_self_contained(self, svg)


if __name__ == "__main__":
    unittest.main()
