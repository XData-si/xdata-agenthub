"""XAH-301: deterministic CLI usability baseline (offline, read-only where possible)."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True, timeout=30)


class UsabilityBaselineTests(unittest.TestCase):
    """Five user tasks: discover, filter, inspect, preview, diagnose."""

    def test_task_1_discover_resources(self):
        result = run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("code-review", result.stdout)

    def test_task_2_filter_and_script_catalog(self):
        first = run_cli("search", "review", "--kind", "skill", "--json")
        second = run_cli("search", "review", "--kind", "skill", "--json")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        records = json.loads(first.stdout)
        self.assertIsInstance(records, list)
        self.assertTrue(records)
        self.assertTrue(all(row["type"] == "skill" for row in records))

    def test_task_3_inspect_provenance_without_writes(self):
        result = run_cli("inspect", "code-review", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload, dict)
        self.assertIn("local_sha256", payload)

    def test_task_4_preview_install_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp)
            before = list(target.rglob("*"))
            result = run_cli("init", "--agent", "claude", "--profile", "developer",
                             "--target", target, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Would install:", result.stdout)
            self.assertEqual(before, list(target.rglob("*")))

    def test_task_5_diagnose_catalog(self):
        result = run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("catalog entries", result.stdout)

    def test_unknown_item_fails_with_actionable_context(self):
        result = run_cli("inspect", "definitely-not-in-catalog")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown item", result.stderr + result.stdout)

    def test_invalid_command_reports_usage(self):
        result = run_cli("not-a-command")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stderr.lower())
