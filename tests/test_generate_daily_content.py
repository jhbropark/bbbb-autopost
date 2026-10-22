"""Regression checks for generated case-study carousel copy."""

import unittest
from dataclasses import replace

from scripts import generate_daily_content as content


class CaseStudySlideTests(unittest.TestCase):
    def test_every_active_topic_has_five_complete_slides(self):
        for topic in content.active_topics():
            self.assertEqual(len(content.CASE_STUDY_SLIDES[topic.slug]), 5, topic.slug)
            for page in range(1, 6):
                copy = content.case_slide_copy(topic, page)
                self.assertEqual(len(copy), 3, (topic.slug, page))
                self.assertTrue(all(isinstance(part, str) and part.strip() for part in copy), (topic.slug, page))

    def test_page_range_is_validated(self):
        topic = content.active_topics()[0]
        for page in (0, 6):
            with self.subTest(page=page), self.assertRaises(ValueError):
                content.case_slide_copy(topic, page)

    def test_unknown_slug_is_reported(self):
        topic = replace(content.active_topics()[0], slug="unknown-topic")
        with self.assertRaisesRegex(KeyError, "unknown-topic"):
            content.case_slide_copy(topic, 1)


if __name__ == "__main__":
    unittest.main()
