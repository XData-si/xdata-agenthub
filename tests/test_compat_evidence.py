import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from compat_evidence import validate_evidence

BASE = ROOT / "tests/fixtures/agent_compatibility_evidence.json"


class CompatibilityEvidenceTests(unittest.TestCase):
    def test_baseline_valid_and_not_claiming_success(self):
        data = json.loads(BASE.read_text(encoding="utf-8"))
        validate_evidence(data)
        self.assertEqual(data["evidence"], [])
        self.assertTrue(all(c["status"] == "not_tested" for c in data["clients"]))

    def test_rejects_unredacted_and_incomplete_evidence(self):
        data = json.loads(BASE.read_text(encoding="utf-8"))
        row = {"client": "claude", "client_version": "example", "os": "linux",
               "os_version": "example", "method": "discovery", "result": "fail",
               "prompt": "List available skills", "steps": ["Launch client"],
               "evidence": "Example only", "redacted": False,
               "timestamp_utc": "2026-10-15T00:00:00Z"}
        data["evidence"] = [row]
        with self.assertRaises(ValueError):
            validate_evidence(data)
        row["redacted"] = True
        validate_evidence(data)
        del row["client_version"]
        with self.assertRaises(ValueError):
            validate_evidence(data)

    def test_rejects_invalid_method(self):
        data = json.loads(BASE.read_text(encoding="utf-8"))
        data["evidence"] = [{"client": "codex", "client_version": "x",
            "os": "windows", "os_version": "11", "method": "imagined",
            "result": "pass", "prompt": "p", "steps": ["s"], "evidence": "e",
            "redacted": True, "timestamp_utc": "2026-10-15T00:00:00Z"}]
        with self.assertRaises(ValueError):
            validate_evidence(data)


if __name__ == "__main__":
    unittest.main()
