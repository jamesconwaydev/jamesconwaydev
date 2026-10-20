import unittest
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from scripts.fonts import text_width
from scripts.header import header_svg
from tests.support import assert_self_contained

COPY = [
    "jamesconwaydev@github: ~",
    "whoami",
    "I build software that solves real problems.",
    "I build software that solves",
    "real problems.",
    "self-hosted business software",
    "high-performance developer tools",
    "linux infrastructure",
]
THEMES = ("dark", "light")


class HeaderTest(unittest.TestCase):
    def test_copy_present(self):
        for theme in THEMES:
            svg = header_svg(theme)
            for text in COPY:
                self.assertIn(escape(text), svg)

    def test_no_external_refs(self):
        for theme in THEMES:
            assert_self_contained(self, header_svg(theme))

    def test_reduced_motion(self):
        self.assertIn("prefers-reduced-motion", header_svg("dark"))

    def test_theme_colours(self):
        self.assertIn("#161b22", header_svg("dark"))
        self.assertIn("#f2f3f5", header_svg("light"))

    def test_headline_fits(self):
        for line in ("I build software that solves", "real problems."):
            self.assertLessEqual(text_width(line, "sans-800", 46, -1.2) + 60, 900 - 60)

    def test_parses(self):
        for theme in THEMES:
            root = ET.fromstring(header_svg(theme))
            self.assertEqual(root.get("role"), "img")
            self.assertEqual(root.get("viewBox").split()[2], "900")
            self.assertTrue(root.get("width") and root.get("height"))

    def test_title(self):
        root = ET.fromstring(header_svg("dark"))
        title = root.find("{http://www.w3.org/2000/svg}title").text
        self.assertEqual(title, "I build software that solves real problems. Self-hosted "
                         "business software, high-performance developer tools, linux infrastructure.")


if __name__ == "__main__":
    unittest.main()
