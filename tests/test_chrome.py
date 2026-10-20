import unittest
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from scripts.chrome import button_svg, footer_svg, icon_svg
from tests.support import assert_self_contained

THEMES = ("dark", "light")
FOLLOW = ("FOLLOW ON GITHUB", "Follow James Conway on GitHub")
STAR = ("STAR A PROJECT BELOW", "Star a project below")


def width(svg):
    return float(ET.fromstring(svg).get("width"))


class ChromeTest(unittest.TestCase):
    def test_icons_parse_both_themes(self):
        for theme in THEMES:
            for name in ("web", "linkedin", "x"):
                root = ET.fromstring(icon_svg(name, theme))
                self.assertEqual((root.get("width"), root.get("height")), ("48", "48"))

    def test_button_width_tracks_label(self):
        short = button_svg("GO", "dark", True)
        long = button_svg("GO AND DO MORE", "dark", True)
        self.assertGreater(width(long), width(short))

    def test_icon_adds_24px(self):
        self.assertAlmostEqual(width(button_svg("GO", "dark", True, "plus")) - width(button_svg("GO", "dark", True)), 24)

    def test_button_label_exact(self):
        for theme in THEMES:
            for label, title, solid, icon in (FOLLOW + (True, "plus"), STAR + (False, "star")):
                svg = button_svg(label, theme, solid, icon)
                ET.fromstring(svg)
                self.assertIn(f">{escape(label)}</text>", svg)
                self.assertIn(f"<title>{escape(title)}</title>", svg)

    def test_star_is_a_shape(self):
        svg = button_svg(STAR[0], "dark", False, "star")
        self.assertNotIn("★", svg)
        self.assertIn("<path", svg)

    def test_footer_has_green_square(self):
        for theme in THEMES:
            svg = footer_svg(theme)
            ET.fromstring(svg)
            self.assertIn("#10b981", svg)

    def test_no_external_refs(self):
        for theme in THEMES:
            for svg in (icon_svg("x", theme), button_svg(FOLLOW[0], theme, True, "plus"), footer_svg(theme)):
                assert_self_contained(self, svg)


if __name__ == "__main__":
    unittest.main()
