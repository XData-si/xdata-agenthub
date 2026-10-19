import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_inspect import inspect_transactions


class RecoveryInspectTests(unittest.TestCase):
    def test_reports_original_and_verified_backup_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src, dest = root / "src", root / "dest"
            src.write_bytes(b"new")
            dest.write_bytes(b"old")
            tx = prepare_journal(root, "test", [("update", src, dest)])
            before = (tx / "journal.json").read_bytes()
            results = inspect_transactions(root)
            self.assertEqual(results[0]["operations"][0]["file_state"], "original")
            self.assertEqual(results[0]["operations"][0]["backup_state"], "verified")
            self.assertEqual((tx / "journal.json").read_bytes(), before)

    def test_detects_modified_destination_and_tampered_backup(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src, dest = root / "src", root / "dest"
            src.write_bytes(b"new")
            dest.write_bytes(b"old")
            tx = prepare_journal(root, "test", [("update", src, dest)])
            dest.write_bytes(b"local edit")
            (tx / "originals" / "0").write_bytes(b"tampered")
            op = inspect_transactions(root)[0]["operations"][0]
            self.assertEqual(op["file_state"], "modified")
            self.assertEqual(op["backup_state"], "tampered")

    def test_rejects_symlinked_store(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            outside = root / "outside"
            outside.mkdir()
            try:
                (root / ".xah-transactions").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable")
            with self.assertRaises(ValueError):
                inspect_transactions(root)


if __name__ == "__main__":
    unittest.main()
