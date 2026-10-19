import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from release_gates import evaluate, REQUIRED

class ReleaseGatesTests(unittest.TestCase):
    def test_missing_evidence_is_not_ready(self):
        self.assertFalse(evaluate({})["ready"])
    def test_all_explicit_passes(self):
        self.assertTrue(evaluate({name: True for name in REQUIRED})["ready"])
    def test_one_failure_blocks(self):
        evidence = {name: True for name in REQUIRED}
        evidence["security_review"] = False
        self.assertFalse(evaluate(evidence)["ready"])
    def test_truthy_string_is_not_pass(self):
        self.assertFalse(evaluate({name: "yes" for name in REQUIRED})["ready"])
