"""Offline tests for native-client test workspace preparation (no client execution)."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/prepare_client_tests.py"


class PrepareClientTests(unittest.TestCase):
    def test_prepares_all_clients_without_marking_pass(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "workspaces"
            p = subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            for client, directory in (("claude", ".claude"), ("codex", ".agents"),
                                      ("opencode", ".opencode")):
                project = out / client
                self.assertTrue((project / directory / "skills/code-review/SKILL.md").is_file())
                self.assertIn("return a - b", (project / "sample.py").read_text())
                template = json.loads((project / "observations.template.json").read_text())
                self.assertEqual(template["client"], client)
                self.assertFalse(template["redaction_reviewed"])
                self.assertEqual(set(template["methods"]), {
                    "discovery", "native_invocation", "direct_read",
                    "negative_missing_file", "negative_unrelated"})
                self.assertTrue(all(v["result"] == "not_tested" for v in template["methods"].values()))

    def test_refuses_nonempty_destination(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "keep.txt").write_text("keep")
            p = subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)],
                               capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual((out / "keep.txt").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
