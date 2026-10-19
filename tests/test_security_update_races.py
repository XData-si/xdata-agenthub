"""XAH-304 SEC-02: deterministic race-window regression tests.

These tests simulate a filesystem change between planning and applying.
They do NOT establish safety against all concurrent writers or symlink swaps.
"""
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
import update_apply
from installed_manifest import _digest, save_manifest


class UpdateRaceRevalidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.destination = self.root / "tracked.txt"
        self.source = self.root / "new.txt"
        self.destination.write_bytes(b"original")
        self.source.write_bytes(b"replacement")
        save_manifest(self.root, {"schema_version": 1, "files": {
            "tracked.txt": {"sha256": _digest(self.destination), "item_id": "test"}}})
        self.manifest_before = (self.root / ".xah-installed.json").read_bytes()

    def inject_after_plan(self, mutate):
        original = update_apply.plan_update

        def wrapper(*args, **kwargs):
            result = original(*args, **kwargs)
            mutate()
            return result

        with patch.object(update_apply, "plan_update", side_effect=wrapper):
            return update_apply.apply_update(self.root, "test",
                                             [(self.source, self.destination)])

    def test_changed_file_after_plan_is_refused(self):
        def change():
            self.destination.write_bytes(b"concurrent user edit")

        with self.assertRaisesRegex(ValueError, "File changed during update"):
            self.inject_after_plan(change)
        self.assertEqual(self.destination.read_bytes(), b"concurrent user edit")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def test_replaced_destination_symlink_after_plan_is_refused(self):
        outside = self.root / "protected.txt"
        outside.write_bytes(b"protected")

        def change():
            self.destination.unlink()
            self.destination.symlink_to(outside)

        try:
            with self.assertRaises(ValueError):
                self.inject_after_plan(change)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this platform")
        self.assertEqual(outside.read_bytes(), b"protected")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def test_untracked_add_destination_appearing_after_plan_is_refused(self):
        added = self.root / "added.txt"

        def change():
            added.write_bytes(b"other process")

        with self.assertRaisesRegex(ValueError, "Destination appeared during update"):
            self.inject_plan_for_add(added, change)
        self.assertEqual(added.read_bytes(), b"other process")
        self.assertEqual((self.root / ".xah-installed.json").read_bytes(), self.manifest_before)

    def inject_plan_for_add(self, added, mutate):
        original = update_apply.plan_update

        def wrapper(*args, **kwargs):
            result = original(*args, **kwargs)
            mutate()
            return result

        with patch.object(update_apply, "plan_update", side_effect=wrapper):
            return update_apply.apply_update(self.root, "test", [(self.source, added)])


if __name__ == "__main__":
    unittest.main()
