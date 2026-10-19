"""Cooperative update lock tests; no external dependencies."""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from update_lock import update_lock
from update_apply import apply_update
from installed_manifest import _digest, save_manifest


class UpdateLockTests(unittest.TestCase):
    def test_second_writer_refused_while_lock_held(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            with update_lock(target):
                with self.assertRaisesRegex(ValueError, "Update lock exists"):
                    with update_lock(target):
                        self.fail("Second writer entered")
            self.assertFalse((target / ".xah-update.lock").exists())

    def test_lock_released_on_exception(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            with self.assertRaises(RuntimeError):
                with update_lock(target):
                    raise RuntimeError("injected")
            self.assertFalse((target / ".xah-update.lock").exists())

    def test_stale_lock_refuses_automatic_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            lock = target / ".xah-update.lock"
            lock.mkdir()
            with self.assertRaisesRegex(ValueError, "Inspect"):
                with update_lock(target):
                    pass
            self.assertTrue(lock.is_dir())

    def test_apply_update_rejects_existing_lock_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            destination = target / "tracked.txt"
            source = target / "new.txt"
            destination.write_bytes(b"old")
            source.write_bytes(b"new")
            save_manifest(target, {"schema_version": 1, "files": {
                "tracked.txt": {"sha256": _digest(destination), "item_id": "test"}}})
            manifest_before = (target / ".xah-installed.json").read_bytes()
            with update_lock(target):
                with self.assertRaisesRegex(ValueError, "Update lock exists"):
                    apply_update(target, "test", [(source, destination)])
            self.assertEqual(destination.read_bytes(), b"old")
            self.assertEqual((target / ".xah-installed.json").read_bytes(), manifest_before)


if __name__ == "__main__":
    unittest.main()
