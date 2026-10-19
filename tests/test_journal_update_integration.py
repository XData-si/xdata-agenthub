"""Update writes must be preceded by a validated prepared-state journal."""
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from installed_manifest import _digest, save_manifest
from recovery_journal import validate_journal
from update_apply import apply_update


class JournalIntegrationTests(unittest.TestCase):
    def fixture(self, root):
        destination = root / "tracked.txt"
        source = root / "replacement.txt"
        destination.write_bytes(b"old")
        source.write_bytes(b"new")
        save_manifest(root, {"schema_version": 1, "files": {
            "tracked.txt": {"sha256": _digest(destination), "item_id": "test"}}})
        return source, destination

    def test_successful_update_prepares_journal_and_original_backup(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, destination = self.fixture(root)
            apply_update(root, "test", [(source, destination)])
            journals = list((root / ".xah-transactions").glob("*/journal.json"))
            self.assertEqual(len(journals), 1)
            metadata = json.loads(journals[0].read_text())
            validate_journal(metadata)
            self.assertEqual(metadata["state"], "prepared")
            self.assertEqual((journals[0].parent / "originals" / "0").read_bytes(), b"old")
            self.assertEqual(destination.read_bytes(), b"new")
            self.assertFalse((root / ".xah-update.lock").exists())

    def test_conflict_creates_no_journal(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, destination = self.fixture(root)
            destination.write_bytes(b"local edit")
            with self.assertRaises(ValueError):
                apply_update(root, "test", [(source, destination)])
            self.assertFalse((root / ".xah-transactions").exists())

    def test_failure_preserves_journal_for_operator_review(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, destination = self.fixture(root)
            with self.assertRaises(RuntimeError):
                apply_update(root, "test", [(source, destination)], fail_after=1)
            self.assertEqual(destination.read_bytes(), b"old")
            journals = list((root / ".xah-transactions").glob("*/journal.json"))
            self.assertEqual(len(journals), 1)
            self.assertEqual(json.loads(journals[0].read_text())["state"], "prepared")


if __name__ == "__main__":
    unittest.main()
