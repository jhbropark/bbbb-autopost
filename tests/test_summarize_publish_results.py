import json
import tempfile
import unittest
from pathlib import Path

from scripts.summarize_publish_results import selected_channels, summarize


class SummarizePublishResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.results_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_result(self, filename, payload):
        (self.results_dir / filename).write_text(json.dumps(payload), encoding="utf-8")

    def test_success_and_error_are_reported_independently(self):
        self.write_result("instagram-publish-results.json", {"instagram": {"id": "receipt-1"}})
        self.write_result("linkedin-publish-results.json", {
            "errors": {"linkedin": {"message": "HTTP 403 with private provider detail"}}
        })

        rows, failures = summarize(self.results_dir, ["instagram", "linkedin_ko"])

        self.assertEqual(failures, 1)
        self.assertEqual(rows[0], ("instagram", "PUBLISHED", "success receipt present"))
        self.assertEqual(rows[1], (
            "linkedin_ko", "FAILED", "HTTP 403; details are in the publish artifact"
        ))

    def test_english_linkedin_uses_its_own_result_file(self):
        self.write_result("linkedin-english-publish-results.json", {"linkedin": {"id": "receipt-en"}})

        rows, failures = summarize(self.results_dir, ["linkedin_en"])

        self.assertEqual(failures, 0)
        self.assertEqual(rows[0][1], "PUBLISHED")

    def test_expected_channel_without_file_fails_closed(self):
        rows, failures = summarize(self.results_dir, ["reddit"])

        self.assertEqual(failures, 1)
        self.assertEqual(rows[0][1], "FAILED")

    def test_failed_publish_step_without_receipt_is_reported(self):
        rows, failures = summarize(self.results_dir, ["x"], {"x": "failure"})

        self.assertEqual(failures, 1)
        self.assertEqual(rows[0][2], "publish step failed; no result receipt")

    def test_unattempted_channel_is_reported_as_skipped(self):
        rows, failures = summarize(self.results_dir, ["instagram_reel"], {"instagram_reel": "skipped"})

        self.assertEqual(failures, 0)
        self.assertEqual(rows[0][1], "SKIPPED")

    def test_publish_scope_maps_english_and_korean_linkedin_separately(self):
        self.assertEqual(selected_channels("workflow_dispatch", "linkedin"), ["linkedin_ko"])
        self.assertEqual(selected_channels("workflow_dispatch", "linkedin_en"), ["linkedin_en"])

    def test_schedule_checks_every_configured_channel(self):
        self.assertEqual(
            selected_channels("schedule", ""),
            ["instagram", "instagram_reel", "facebook", "linkedin_ko", "linkedin_en", "x", "reddit"],
        )

    def test_skipped_channel_is_not_reported_as_published_or_failed(self):
        self.write_result("instagram-publish-results.json", {
            "instagram": {"status": "skipped", "reason": "duplicate_caption"}
        })

        rows, failures = summarize(self.results_dir, ["instagram"])

        self.assertEqual(failures, 0)
        self.assertEqual(rows[0][1], "SKIPPED")

    def test_invalid_json_fails_closed(self):
        (self.results_dir / "x-publish-results.json").write_text("{bad", encoding="utf-8")

        rows, failures = summarize(self.results_dir, ["x"])

        self.assertEqual(failures, 1)
        self.assertEqual(rows[0][1], "FAILED")

    def test_failure_detail_does_not_echo_provider_payload(self):
        self.write_result("reddit-publish-results.json", {
            "errors": {"reddit": {"message": "Missing required environment variable: REDDIT_SUBREDDIT"}}
        })

        rows, _ = summarize(self.results_dir, ["reddit"])

        self.assertEqual(rows[0][2], "required configuration is missing")
        self.assertNotIn("REDDIT_SUBREDDIT", rows[0][2])


if __name__ == "__main__":
    unittest.main()
