"""End-to-end writer guard regression tests for unresolved journals."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from installed_manifest import _digest, save_manifest
from journal_prepare import prepare_journal
from recovery_journal import transition_journal
from update_apply import apply_update


class PendingJournalIntegrationTests(unittest.TestCase):
    def fixture(self, root):
        dest, source = root / "tracked.txt", root / "source.txt"
        dest.write_bytes(b"old")
        source.write_bytes(b"new")
        save_manifest(root, {"schema_version": 1, "files": {
            "tracked.txt": {"sha256": _digest(dest), "item_id": "test"}}})
        return source, dest

    def test_update_refuses_prepared_transaction_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, dest = self.fixture(root)
            tx = prepare_journal(root, "test", [("update", source, dest)])
            before = (root / ".xah-installed.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "Unresolved XAH transaction"):
                apply_update(root, "test", [(source, dest)])
            self.assertEqual(dest.read_bytes(), b"old")
            self.assertEqual((root / ".xah-installed.json").read_bytes(), before)
            self.assertEqual(len(list((root / ".xah-transactions").iterdir())), 1)
            self.assertFalse((root / ".xah-update.lock").exists())
            self.assertTrue((tx / "journal.json").exists())

    def test_update_refuses_recovery_required_transaction(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, dest = self.fixture(root)
            tx = prepare_journal(root, "test", [("update", source, dest)])
            transition_journal(tx, "recovery_required")
            with self.assertRaisesRegex(ValueError, "Unresolved XAH transaction"):
                apply_update(root, "test", [(source, dest)])
            self.assertEqual(dest.read_bytes(), b"old")

    def test_committed_transaction_allows_next_update(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            source, dest = self.fixture(root)
            apply_update(root, "test", [(source, dest)])
            self.assertEqual(dest.read_bytes(), b"new")
            source.write_bytes(b"newer")
            apply_update(root, "test", [(source, dest)])
            self.assertEqual(dest.read_bytes(), b"newer")
            self.assertEqual(len(list((root / ".xah-transactions").iterdir())), 2)


if __name__ == "__main__":
    unittest.main()
