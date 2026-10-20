import unittest

from scripts.theme import FONTS, THEMES

KEYS = {"bg", "panel", "line", "ink", "muted", "green", "orange"}


class ThemeTests(unittest.TestCase):
    def test_both_themes_share_keys(self):
        self.assertEqual(THEMES["dark"].keys(), THEMES["light"].keys())
        self.assertEqual(set(THEMES["dark"]), KEYS)

    def test_brand_values(self):
        for theme in THEMES.values():
            self.assertEqual(theme["green"], "#10b981")
            self.assertEqual(theme["orange"], "#e8913f")
        self.assertEqual(THEMES["dark"]["bg"], "#0d1117")
        self.assertEqual(THEMES["light"]["bg"], "#ffffff")

    def test_font_files_exist(self):
        self.assertEqual(set(FONTS), {"sans-400", "sans-800", "mono-500", "mono-600"})
        for path in FONTS.values():
            self.assertTrue(path.is_file(), path)


if __name__ == "__main__":
    unittest.main()
