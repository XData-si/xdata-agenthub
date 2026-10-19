import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_inspect import inspect_transactions


class RecoveryInspectionHardeningTests(unittest.TestCase):
    def fixture(self, root):
        src, dest = root / "source", root / "dest"
        src.write_bytes(b"new")
        dest.write_bytes(b"old")
        return prepare_journal(root, "test", [("update", src, dest)])

    def test_symlinked_originals_directory_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx = self.fixture(root)
            original_dir = tx / "originals"
            original_dir.rename(tx / "real-originals")
            try:
                original_dir.symlink_to(tx / "real-originals", target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable")
            with self.assertRaisesRegex(ValueError, "Unsafe originals directory"):
                inspect_transactions(root)

    def test_oversized_journal_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx = self.fixture(root)
            (tx / "journal.json").write_bytes(b" " * 2_000_001)
            with self.assertRaisesRegex(ValueError, "Oversized transaction journal"):
                inspect_transactions(root)


if __name__ == "__main__":
    unittest.main()
