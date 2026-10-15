import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"

class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)

    def test_catalog_paths(self):
        for item in json.loads((ROOT / "registry/catalog.json").read_text())["items"]:
            self.assertTrue((ROOT / item["path"]).is_file())

    def test_list(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("code-review", result.stdout)

    def test_add_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_cli("add", "code-review", "--target", tmp).returncode, 0)
            self.assertNotEqual(self.run_cli("add", "code-review", "--target", tmp).returncode, 0)

    def test_doctor(self):
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("catalog entries", result.stdout)

    def test_init_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("init", "--target", tmp, "--profile", "developer", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((pathlib.Path(tmp) / "instructions/AGENTS.md").exists())

    def test_init_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("init", "--target", tmp, "--profile", "research")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((pathlib.Path(tmp) / "agents/research-agent.md").exists())
            second = self.run_cli("init", "--target", tmp, "--profile", "research")
            self.assertNotEqual(second.returncode, 0)

if __name__ == "__main__":
    unittest.main()
