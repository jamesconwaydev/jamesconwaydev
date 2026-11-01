import unittest
import xml.etree.ElementTree as ET

from scripts.feature import OrgCounts, feature_svg
from tests.support import assert_self_contained


class FeatureTest(unittest.TestCase):
    def test_one_light_per_circuit_and_room_for_more(self):
        small, big = feature_svg(OrgCounts(106, 50), "dark"), feature_svg(OrgCounts(130, 125), "dark")
        self.assertEqual(small.count('class="led"'), 50)
        self.assertEqual(big.count('class="led"'), 125)
        self.assertGreater(int(ET.fromstring(big).get("height")), int(ET.fromstring(small).get("height")))

    def test_says_both_sides_and_is_self_contained(self):
        for theme in ("dark", "light"):
            svg = feature_svg(OrgCounts(106, 101), theme)
            assert_self_contained(self, svg)
            for text in ("INFRASTRUCTURE AS CODE", "CONFIGURATION MANAGEMENT", ">101<", ">106<", "prefers-reduced-motion"):
                self.assertIn(text, svg)


if __name__ == "__main__":
    unittest.main()
