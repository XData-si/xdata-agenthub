import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_journal import transition_journal
from recovery_resolution_preflight import resolution_preflight


class ResolutionPreflightTests(unittest.TestCase):
    def fixture(self, root):
        src, dest = root / "src", root / "dest"
        src.write_bytes(b"new")
        dest.write_bytes(b"old")
        tx = prepare_journal(root, "test", [("update", src, dest)])
        transition_journal(tx, "recovery_required")
        return tx, dest

    def test_original_file_passes_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            result = resolution_preflight(root, tx.name)
            self.assertTrue(result["files_restored"])
            self.assertFalse(result["manifest_verified"])
            self.assertEqual(dest.read_bytes(), b"old")

    def test_intended_file_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            dest.write_bytes(b"new")
            with self.assertRaisesRegex(ValueError, "not restored"):
                resolution_preflight(root, tx.name)

    def test_modified_file_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            dest.write_bytes(b"local edit")
            with self.assertRaisesRegex(ValueError, "not restored"):
                resolution_preflight(root, tx.name)

    def test_bad_backup_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            (tx / "originals" / "0").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "backup integrity"):
                resolution_preflight(root, tx.name)


if __name__ == "__main__":
    unittest.main()
