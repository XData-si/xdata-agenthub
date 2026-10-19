import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from release_gates import evaluate, REQUIRED


def approved():
    return {name: {"passed": True, "reference": "https://example.org/evidence/" + name,
                   "reviewer": "release-reviewer"} for name in REQUIRED}


class ReleaseGatesTests(unittest.TestCase):
    def test_missing_evidence_is_not_ready(self):
        self.assertFalse(evaluate({})["ready"])

    def test_all_explicit_reviewed_references(self):
        self.assertTrue(evaluate(approved())["ready"])

    def test_one_failure_blocks(self):
        evidence = approved()
        evidence["security_review"]["passed"] = False
        self.assertFalse(evaluate(evidence)["ready"])

    def test_truthy_string_is_not_pass(self):
        self.assertFalse(evaluate({name: "yes" for name in REQUIRED})["ready"])

    def test_boolean_without_reference_is_not_pass(self):
        self.assertFalse(evaluate({name: True for name in REQUIRED})["ready"])

    def test_missing_reviewer_blocks(self):
        evidence = approved()
        evidence["ci_matrix"].pop("reviewer")
        self.assertFalse(evaluate(evidence)["ready"])

    def test_blank_reference_blocks(self):
        evidence = approved()
        evidence["documentation"]["reference"] = " "
        self.assertFalse(evaluate(evidence)["ready"])
