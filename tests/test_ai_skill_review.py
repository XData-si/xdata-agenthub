"""Offline tests for the advisory AI review: parsing is fail-safe and output is neutralized."""
import os
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ai_skill_review as review  # noqa: E402


class ParseReviewTests(unittest.TestCase):
    def test_malformed_output_is_never_a_pass(self):
        self.assertEqual(review.parse_review("I think it is fine")["verdict"], "needs_review")
        self.assertEqual(review.parse_review('{"verdict": "approve"}')["verdict"], "needs_review")

    def test_high_security_finding_downgrades_pass(self):
        raw = '{"verdict": "pass", "findings": [{"severity": "critical", "category": "security", "evidence": "x", "explanation": "y"}]}'
        self.assertEqual(review.parse_review(raw)["verdict"], "needs_review")

    def test_block_is_preserved_and_fields_are_bounded(self):
        raw = '{"verdict": "block", "summary": "' + "s" * 1000 + '", "findings": [{"severity": "weird", "category": "x"}]}'
        parsed = review.parse_review(raw)
        self.assertEqual(parsed["verdict"], "block")
        self.assertLessEqual(len(parsed["summary"]), 300)
        self.assertEqual(parsed["findings"][0]["severity"], "medium")

    def test_render_neutralizes_mentions_html_and_links(self):
        text = review.render({"demo": {"verdict": "pass", "summary": "@maintainers <img src=x> [x](https://e.vil)",
                                       "findings": [], "eu_ready": True, "eu_notes": ""}}, "m")
        self.assertNotIn("@maintainers", text)
        self.assertNotIn("<img", text)
        self.assertNotIn("](https://e.vil)", text)

    def test_skips_without_configuration(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("AI_REVIEW_")}
        result = subprocess.run([sys.executable, str(ROOT / "scripts/ai_skill_review.py"), "code-review"],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("skipped", result.stdout)


if __name__ == "__main__":
    unittest.main()
