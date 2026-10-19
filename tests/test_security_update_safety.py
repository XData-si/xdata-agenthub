"""XAH-304: conflict handling and rollback security regression tests."""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from installed_manifest import _digest, save_manifest
from update_apply import apply_update
from update_plan import plan_update


class UpdateSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.dest = self.root / "tracked.txt"
        self.src = self.root / "incoming.txt"
        self.dest.write_bytes(b"old")
        self.src.write_bytes(b"new")
        save_manifest(self.root, {"schema_version": 1, "files": {
            "tracked.txt": {"sha256": _digest(self.dest), "item_id": "test"}}})
        self.manifest_before = (self.root / ".xah-installed.json").read_bytes()

    def test_dry_run_does_not_write(self):
        self.assertEqual(plan_update(self.root, "test", [(self.src, self.dest)]),
                         [("update", "tracked.txt")])
        self.assertEqual(self.dest.read_bytes(), b"old")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def test_local_modification_conflicts_and_preserves_manifest(self):
        self.dest.write_bytes(b"local edit")
        self.assertEqual(plan_update(self.root, "test", [(self.src, self.dest)]),
                         [("conflict", "tracked.txt")])
        with self.assertRaises(ValueError):
            apply_update(self.root, "test", [(self.src, self.dest)])
        self.assertEqual(self.dest.read_bytes(), b"local edit")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def test_item_ownership_conflict_refuses_update(self):
        save_manifest(self.root, {"schema_version": 1, "files": {
            "tracked.txt": {"sha256": _digest(self.dest), "item_id": "other"}}})
        before = (self.root / ".xah-installed.json").read_bytes()
        with self.assertRaises(ValueError):
            apply_update(self.root, "test", [(self.src, self.dest)])
        self.assertEqual(self.dest.read_bytes(), b"old")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), before)

    def test_injected_failure_restores_bytes_and_manifest(self):
        with self.assertRaises(RuntimeError):
            apply_update(self.root, "test", [(self.src, self.dest)], fail_after=1)
        self.assertEqual(self.dest.read_bytes(), b"old")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def test_existing_untracked_file_refused(self):
        untracked = self.root / "untracked.txt"
        untracked.write_bytes(b"user data")
        with self.assertRaises(ValueError):
            apply_update(self.root, "test", [(self.src, untracked)])
        self.assertEqual(untracked.read_bytes(), b"user data")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def test_missing_tracked_file_is_conflict(self):
        self.dest.unlink()
        with self.assertRaises(ValueError):
            apply_update(self.root, "test", [(self.src, self.dest)])
        self.assertFalse(self.dest.exists())
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)


if __name__ == "__main__":
    unittest.main()
