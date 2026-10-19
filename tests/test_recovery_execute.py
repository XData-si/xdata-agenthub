import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from installed_manifest import _digest, load_manifest, save_manifest
from recovery_execute import rollback_transaction
from recovery_guard import require_no_pending_transactions
from update_apply import apply_update
from journal_prepare import prepare_journal
from recovery_journal import transition_journal


class RecoveryExecuteTests(unittest.TestCase):
    def fixture(self, root):
        source, dest = root / "source", root / "tracked"
        source.write_bytes(b"new")
        dest.write_bytes(b"old")
        save_manifest(root, {"schema_version": 1, "files": {
            "tracked": {"sha256": _digest(dest), "item_id": "test"}}})
        tx = prepare_journal(root, "test", [("update", source, dest)])
        transition_journal(tx, "applying")
        return tx, source, dest

    def test_restores_intended_update_and_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, source, dest = self.fixture(root)
            dest.write_bytes(b"new")
            save_manifest(root, {"schema_version": 1, "files": {
                "tracked": {"sha256": _digest(dest), "item_id": "test"}}})
            result = rollback_transaction(root, tx.name)
            self.assertEqual(result["state"], "resolved")
            self.assertEqual(dest.read_bytes(), b"old")
            self.assertEqual(load_manifest(root)["files"]["tracked"]["sha256"], _digest(dest))
            require_no_pending_transactions(root)

    def test_refuses_modified_destination(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, source, dest = self.fixture(root)
            dest.write_bytes(b"user edit")
            with self.assertRaisesRegex(ValueError, "Unsafe update"):
                rollback_transaction(root, tx.name)
            self.assertEqual(dest.read_bytes(), b"user edit")

    def test_refuses_existing_writer_lock(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, source, dest = self.fixture(root)
            (root / ".xah-update.lock").mkdir()
            with self.assertRaisesRegex(ValueError, "Update lock exists"):
                rollback_transaction(root, tx.name)
            self.assertTrue((root / ".xah-update.lock").exists())

    def test_already_restored_update_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, source, dest = self.fixture(root)
            result = rollback_transaction(root, tx.name)
            self.assertEqual(result["state"], "resolved")
            self.assertEqual(dest.read_bytes(), b"old")

    def test_added_file_is_removed_only_if_intended(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src, dest = root / "src", root / "added"
            src.write_bytes(b"new")
            tx = prepare_journal(root, "test", [("add", src, dest)])
            transition_journal(tx, "applying")
            dest.write_bytes(b"new")
            result = rollback_transaction(root, tx.name)
            self.assertEqual(result["state"], "resolved")
            self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
