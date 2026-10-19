"""Cross-feature CLI smoke tests for the integrated XAH 0.3 candidate."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"


def invoke(*args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          text=True, capture_output=True, cwd=ROOT)


class IntegratedCliTests(unittest.TestCase):
    def test_browse_json(self):
        result = invoke("browse", "--kind", "skill", "--limit", "2", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(len(data["items"]), 2)
        self.assertIn("facets", data)

    def test_trust_json(self):
        result = invoke("trust", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout))

    def test_release_check_missing_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "evidence.json"
            path.write_text("{}", encoding="utf-8")
            result = invoke("release-check", "--evidence", str(path), "--json")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(json.loads(result.stdout)["ready"])

    def test_recovery_resolution_option_is_registered(self):
        result = invoke("recovery", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--resolution-check", result.stdout)

    def test_adapter_install_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = invoke("init", "--agent", "claude", "--target", tmp, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(".claude", result.stdout)
