import unittest

from scripts.fonts import font_face_css, text_width


class FontsTest(unittest.TestCase):
    def test_width_grows_with_text(self):
        self.assertGreater(text_width("ab", "sans-800", 20), text_width("a", "sans-800", 20))

    def test_mono_is_fixed_pitch(self):
        self.assertEqual(text_width("iii", "mono-500", 10), text_width("WWW", "mono-500", 10))

    def test_letter_spacing_added(self):
        spaced = text_width("ab", "mono-500", 10, 2)
        self.assertAlmostEqual(spaced - text_width("ab", "mono-500", 10), 2)

    def test_css_embeds_only_used_fonts(self):
        css = font_face_css({"mono-500": "$"})
        self.assertIn('"M500"', css)
        self.assertIn("data:font/woff2;base64,", css)
        self.assertNotIn('"S800"', css)

    def test_subset_is_small(self):
        self.assertLess(len(font_face_css({"mono-500": "$"})), 8 * 1024)

    def test_missing_glyph_raises(self):
        with self.assertRaisesRegex(ValueError, "mono-500"):
            font_face_css({"mono-500": "★"})
        with self.assertRaises(ValueError):
            text_width("★", "mono-500", 10)

    def test_deterministic(self):
        usage = {"sans-800": "Hello", "mono-600": "$ ls"}
        self.assertEqual(font_face_css(usage), font_face_css(usage))


if __name__ == "__main__":
    unittest.main()
