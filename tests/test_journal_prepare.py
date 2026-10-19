import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_journal import validate_journal


class JournalPrepareTests(unittest.TestCase):
    def test_prepare_preserves_destination_and_backs_up_original(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            dest, source = root / "tracked.txt", root / "new.txt"
            dest.write_bytes(b"original")
            source.write_bytes(b"replacement")
            tx = prepare_journal(root, "test", [("update", source, dest)])
            data = json.loads((tx / "journal.json").read_text())
            validate_journal(data)
            self.assertEqual(data["state"], "prepared")
            self.assertEqual((tx / "originals" / "0").read_bytes(), b"original")
            self.assertEqual(dest.read_bytes(), b"original")

    def test_add_has_no_backup_and_does_not_install(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, dest = root / "source", root / "destination"
            source.write_bytes(b"content")
            tx = prepare_journal(root, "test", [("add", source, dest)])
            data = json.loads((tx / "journal.json").read_text())
            self.assertIsNone(data["operations"][0]["backup_sha256"])
            self.assertFalse((tx / "originals" / "0").exists())
            self.assertFalse(dest.exists())

    def test_traversal_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source = root / "source"
            source.write_bytes(b"content")
            with self.assertRaises(ValueError):
                prepare_journal(root, "test", [("add", source, root / ".." / "escape")])
            self.assertFalse((root / ".xah-transactions").exists())

    def test_symlink_store_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            outside = root / "outside"
            outside.mkdir()
            try:
                (root / ".xah-transactions").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable")
            source = root / "source"
            source.write_bytes(b"content")
            with self.assertRaises(ValueError):
                prepare_journal(root, "test", [("add", source, root / "destination")])
            self.assertEqual(list(outside.iterdir()), [])

    def test_duplicate_paths_refused_before_store_creation(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source = root / "source"
            source.write_bytes(b"content")
            dest = root / "dest"
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                prepare_journal(root, "test", [("add", source, dest), ("add", source, dest)])
            self.assertFalse((root / ".xah-transactions").exists())


if __name__ == "__main__":
    unittest.main()
