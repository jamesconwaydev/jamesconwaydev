import datetime
import unittest
import urllib.error
from unittest import mock

from scripts.feed import Post, fetch_feed, parse_feed, posts_markdown, replace_block
from scripts.theme import ROOT

XML = (ROOT / "tests" / "fixtures" / "rss.xml").read_text(encoding="utf-8")


class FeedTests(unittest.TestCase):
    def test_newest_three(self):
        posts = parse_feed(XML)
        self.assertEqual(len(posts), 3)
        self.assertEqual(posts[0].title, "Apparently, I Don't Know How to Build Small Projects")
        self.assertEqual(posts[0].date, datetime.date(2026, 10, 10))
        self.assertEqual([p.date for p in posts], sorted((p.date for p in posts), reverse=True))

    def test_mixed_timezones_sort(self):
        item = lambda t, d: f"<item><title>{t}</title><link>u</link><description>s</description><pubDate>{d}</pubDate></item>"
        xml = ("<rss><channel>" + item("naive", "Mon, 05 Oct 2026 10:00:00 -0000")
               + item("aware", "Tue, 06 Oct 2026 10:00:00 GMT") + "</channel></rss>")
        self.assertEqual([p.title for p in parse_feed(xml)], ["aware", "naive"])

    def test_entities_decoded(self):
        for p in parse_feed(XML):
            self.assertNotIn("&apos;", p.title + p.summary)
        self.assertIn("'", parse_feed(XML)[0].title)

    def test_markdown_escaped(self):
        post = Post("a [b] *c*", "https://x.test/", datetime.date(2026, 1, 2), "s_1 <i> \\")
        md = posts_markdown([post])
        self.assertIn(r"a \[b\] \*c\*", md)
        self.assertIn(r"s\_1 \<i\> \\", md)
        self.assertIn("`2026-01-02` · **[", md)
        self.assertTrue(md.endswith("[Read the rest on jamesconway.dev →](https://jamesconway.dev/blog/)"))

    def test_replace_block_idempotent(self):
        readme = "top\n<!-- BLOG:START -->\nold\n<!-- BLOG:END -->\nbottom\n"
        once = replace_block(readme, "new")
        self.assertEqual(once, "top\n<!-- BLOG:START -->\nnew\n<!-- BLOG:END -->\nbottom\n")
        self.assertEqual(replace_block(once, "new"), once)

    def test_missing_marker_raises(self):
        with self.assertRaises(ValueError):
            replace_block("<!-- BLOG:START -->\nno end", "x")
        with self.assertRaises(ValueError):
            replace_block("no markers", "x", name="CARDS")

    def test_empty_feed_raises(self):
        with self.assertRaises(ValueError):
            parse_feed('<rss version="2.0"><channel><title>t</title></channel></rss>')

    def test_fetch_failure_raises(self):
        for err in (urllib.error.HTTPError("u", 503, "x", {}, None), urllib.error.URLError("down"), TimeoutError("slow")):
            with mock.patch("urllib.request.urlopen", side_effect=err):
                with self.assertRaises(RuntimeError):
                    fetch_feed()

    def test_fetch_non_200_raises(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value.status = 204
        with mock.patch("urllib.request.urlopen", return_value=resp):
            with self.assertRaises(RuntimeError):
                fetch_feed()


if __name__ == "__main__":
    unittest.main()
