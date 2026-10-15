import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from installed_manifest import file_states, load_manifest, MANIFEST_NAME


class InstalledManifestTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "cli/xah.py"), *args], capture_output=True, text=True)

    def test_add_and_detect_changes(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            result = self.cli("add", "code-review", "--target", d)
            self.assertEqual(result.returncode, 0, result.stderr)
            rel = ".agents/skills/code-review/SKILL.md" if False else "skills/code-review/SKILL.md"
            self.assertEqual(file_states(target)[rel], "untouched")
            (target / rel).write_text("local changes", encoding="utf-8")
            self.assertEqual(file_states(target)[rel], "modified")
            (target / rel).unlink()
            self.assertEqual(file_states(target)[rel], "missing")
            status = self.cli("status", "--target", d)
            self.assertIn("missing", status.stdout)

    def test_manifest_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            external = target / "external"
            external.write_text("{}", encoding="utf-8")
            (target / MANIFEST_NAME).symlink_to(external)
            self.assertNotEqual(self.cli("add", "code-review", "--target", d).returncode, 0)

    def test_init_tracks_all_files(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.cli("init", "--target", d).returncode, 0)
            manifest = load_manifest(pathlib.Path(d))
            self.assertGreaterEqual(len(manifest["files"]), 3)
            self.assertTrue(all(v == "untouched" for v in file_states(pathlib.Path(d)).values()))


if __name__ == "__main__":
    unittest.main()
