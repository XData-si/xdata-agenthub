import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from recovery_lock_inspect import inspect_writer_lock


class LockInspectionTests(unittest.TestCase):
    def test_absent_lock(self):
        with tempfile.TemporaryDirectory() as d:
            result = inspect_writer_lock(d)
            self.assertEqual(result["status"], "absent")
            self.assertFalse(result["removal_safe"])

    def test_existing_process_does_not_authorize_removal(self):
        with tempfile.TemporaryDirectory() as d:
            lock = pathlib.Path(d) / ".xah-update.lock"
            lock.mkdir()
            (lock / "pid").write_text(str(os.getpid()), encoding="ascii")
            result = inspect_writer_lock(d)
            self.assertFalse(result["removal_safe"])
            self.assertTrue(lock.exists())

    def test_invalid_pid_refused(self):
        with tempfile.TemporaryDirectory() as d:
            lock = pathlib.Path(d) / ".xah-update.lock"
            lock.mkdir()
            (lock / "pid").write_text("not-a-pid", encoding="ascii")
            result = inspect_writer_lock(d)
            self.assertEqual(result["status"], "unverifiable")
            self.assertTrue(lock.exists())

    def test_symlinked_lock_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            actual = root / "real"
            actual.mkdir()
            try:
                (root / ".xah-update.lock").symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable")
            result = inspect_writer_lock(root)
            self.assertEqual(result["status"], "unsafe_symlink")
            self.assertFalse(result["removal_safe"])


if __name__ == "__main__":
    unittest.main()
