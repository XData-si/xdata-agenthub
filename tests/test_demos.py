"""Before/after demos: the rubric is well formed, the fixtures exist and committed results score reproducibly."""
import json
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "demos"))
import score  # noqa: E402


class DemoTests(unittest.TestCase):
    def test_rubric_patterns_compile_and_fixtures_exist(self):
        rubric = json.loads((ROOT / "demos/rubric.json").read_text(encoding="utf-8"))["demos"]
        for name, spec in rubric.items():
            self.assertTrue((ROOT / "demos" / spec["fixture"]).is_dir(), name)
            self.assertTrue((ROOT / "skills" / spec["skill"] / "SKILL.md").is_file(), name)
            self.assertNotIn(spec["skill"], spec["prompt"], "prompts must not name the skill")
            for patterns in spec["items"].values():
                for pattern in patterns:
                    re.compile(pattern)

    def test_overrides_are_applied_and_scoring_is_per_condition(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = pathlib.Path(tmp)
            (results / "answers").mkdir()
            (results / "answers/review-baseline-1.txt").write_text("SQL injection on line 12.", encoding="utf-8")
            (results / "answers/review-skill-1.txt").write_text("Injection; IDOR; off-by-one.", encoding="utf-8")
            (results / "metrics.json").write_text(json.dumps({"review-skill-1": {"skill_calls": ["code-review"]}}))
            item = "R4 Authorization header logged"
            rubric, runs = score.score(results, {"review-baseline-1": {item: True, "reason": "test"}})
            self.assertTrue(runs["review-baseline-1"]["found"][item])
            self.assertFalse(runs["review-skill-1"]["found"][item])
            rows = {r["condition"]: r for r in score.summary(rubric, runs) if r["demo"] == "review"}
            self.assertEqual(rows["skill"]["skill_loaded"], 1)
            self.assertEqual(rows["baseline"]["skill_loaded"], 0)

    def test_committed_results_match_published_report(self):
        results = ROOT / "demos/results/2026-10-29"
        overrides = json.loads((results / "overrides.json").read_text(encoding="utf-8"))
        rubric, runs = score.score(results, overrides)
        table = score.markdown(rubric, score.summary(rubric, runs)).split("\n\n")[0]
        self.assertIn(table, (results / "RESULTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
