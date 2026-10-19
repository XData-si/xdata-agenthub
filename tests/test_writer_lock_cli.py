"""All mutating CLI install commands respect the cooperative writer lock."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"


class WriterLockCLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                              capture_output=True, text=True, timeout=30)

    def test_add_refuses_existing_lock_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            (target / ".xah-update.lock").mkdir()
            result = self.run_cli("add", "code-review", "--target", target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Update lock exists", result.stderr)
            self.assertFalse((target / "skills").exists())
            self.assertFalse((target / ".xah-installed.json").exists())

    def test_init_refuses_existing_lock_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            (target / ".xah-update.lock").mkdir()
            result = self.run_cli("init", "--profile", "developer", "--target", target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Update lock exists", result.stderr)
            self.assertFalse((target / "skills").exists())
            self.assertFalse((target / ".xah-installed.json").exists())

    def test_successful_add_releases_lock(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            result = self.run_cli("add", "code-review", "--target", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((target / ".xah-update.lock").exists())

    def test_successful_init_releases_lock(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            result = self.run_cli("init", "--profile", "developer", "--target", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((target / ".xah-update.lock").exists())


if __name__ == "__main__":
    unittest.main()
