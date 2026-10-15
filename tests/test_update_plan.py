import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli/xah.py"


class UpdatePlanTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)

    def test_read_only_skip_and_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            self.assertEqual(self.cli("add", "code-review", "--target", d).returncode, 0)
            manifest = root / ".xah-installed.json"
            before = manifest.read_bytes()
            first = self.cli("update", "code-review", "--target", d, "--dry-run")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("skip", first.stdout)
            self.assertEqual(manifest.read_bytes(), before)
            skill = root / "skills/code-review/SKILL.md"
            skill.write_text("custom local edit", encoding="utf-8")
            second = self.cli("update", "code-review", "--target", d, "--dry-run")
            self.assertEqual(second.returncode, 2, second.stderr)
            self.assertIn("conflict", second.stdout)
            self.assertEqual(skill.read_text(), "custom local edit")
            self.assertEqual(manifest.read_bytes(), before)

    def test_add_preview_and_unmanaged_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            first = self.cli("update", "code-review", "--target", d, "--dry-run")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("add", first.stdout)
            self.assertFalse((root / ".xah-installed.json").exists())
            p = root / "skills/code-review/SKILL.md"
            p.parent.mkdir(parents=True)
            p.write_text("unmanaged", encoding="utf-8")
            second = self.cli("update", "code-review", "--target", d, "--dry-run")
            self.assertEqual(second.returncode, 2, second.stderr)
            self.assertIn("conflict", second.stdout)
            self.assertEqual(p.read_text(), "unmanaged")


if __name__ == "__main__":
    unittest.main()
