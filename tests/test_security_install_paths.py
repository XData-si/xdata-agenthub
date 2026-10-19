"""XAH-304 SEC-01: offline path traversal and symlink regression tests."""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from installed_manifest import _relative, load_manifest
from update_plan import plan_update


class InstallPathSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = pathlib.Path(self.tmp.name)
        self.target = self.base / "project"
        self.target.mkdir()
        self.outside = self.base / "outside"
        self.outside.mkdir()

    def symlink_or_skip(self, link, destination):
        try:
            link.symlink_to(destination, target_is_directory=destination.is_dir())
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable on this platform")

    def test_reject_parent_traversal(self):
        with self.assertRaises(ValueError):
            _relative(self.target, self.target / ".." / "outside" / "escaped.md")

    def test_reject_absolute_destination_outside_target(self):
        with self.assertRaises(ValueError):
            _relative(self.target, self.outside / "escaped.md")

    def test_reject_symlinked_parent_directory(self):
        self.symlink_or_skip(self.target / "skills", self.outside)
        with self.assertRaises(ValueError):
            _relative(self.target, self.target / "skills" / "escaped.md")

    def test_reject_symlinked_destination_file(self):
        protected = self.outside / "protected.md"
        protected.write_text("do not touch")
        self.symlink_or_skip(self.target / "skill.md", protected)
        with self.assertRaises(ValueError):
            _relative(self.target, self.target / "skill.md")
        self.assertEqual(protected.read_text(), "do not touch")

    def test_reject_symlinked_installed_manifest(self):
        protected = self.outside / "manifest.json"
        protected.write_text('{"schema_version":1,"files":{}}')
        self.symlink_or_skip(self.target / ".xah-installed.json", protected)
        with self.assertRaises(ValueError):
            load_manifest(self.target)
        self.assertEqual(protected.read_text(), '{"schema_version":1,"files":{}}')

    def test_update_planner_rejects_escaping_destination(self):
        source = self.base / "source.md"
        source.write_text("sample")
        with self.assertRaises(ValueError):
            plan_update(self.target, "code-review", [(source, self.outside / "escaped.md")])
        self.assertFalse((self.outside / "escaped.md").exists())

    def test_update_planner_rejects_symlinked_parent(self):
        source = self.base / "source.md"
        source.write_text("sample")
        self.symlink_or_skip(self.target / "skills", self.outside)
        with self.assertRaises(ValueError):
            plan_update(self.target, "code-review", [(source, self.target / "skills" / "escaped.md")])
        self.assertFalse((self.outside / "escaped.md").exists())


if __name__ == "__main__":
    unittest.main()
