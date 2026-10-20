"""Assertions shared by the SVG generator tests."""
import re

SVG_NS = "http://www.w3.org/2000/svg"


def assert_self_contained(testcase, svg: str) -> None:
    """GitHub serves these through <img>, so nothing may reach outside the file."""
    testcase.assertNotIn("<script", svg)
    testcase.assertNotIn("@import", svg)
    testcase.assertEqual(re.findall(r"https?://[^\s\"'<>)]*", svg.replace(SVG_NS, "")), [])
    for ref in re.findall(r"url\(\s*['\"]?([^'\")]*)", svg):
        testcase.assertTrue(ref.startswith(("data:", "#")), f"external url({ref})")
