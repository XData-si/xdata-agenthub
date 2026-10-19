import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_journal import transition_journal
from recovery_preflight import rollback_preflight


class RecoveryPreflightTests(unittest.TestCase):
    def setup_tx(self, root, action="update"):
        source, dest = root / "source", root / "destination"
        source.write_bytes(b"new")
        if action == "update":
            dest.write_bytes(b"old")
        tx = prepare_journal(root, "test", [(action, source, dest)])
        transition_journal(tx, "applying")
        return tx, dest

    def test_intended_update_plans_restore_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.setup_tx(root)
            dest.write_bytes(b"new")
            result = rollback_preflight(root, tx.name)
            self.assertEqual(result["operations"][0]["action"], "restore_original")
            self.assertEqual(dest.read_bytes(), b"new")

    def test_modified_update_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.setup_tx(root)
            dest.write_bytes(b"user edit")
            with self.assertRaisesRegex(ValueError, "unknown destination"):
                rollback_preflight(root, tx.name)
            self.assertEqual(dest.read_bytes(), b"user edit")

    def test_tampered_backup_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.setup_tx(root)
            (tx / "originals" / "0").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "backup is not verified"):
                rollback_preflight(root, tx.name)

    def test_committed_transaction_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.setup_tx(root)
            transition_journal(tx, "applying", completed=0)
            transition_journal(tx, "committed")
            with self.assertRaisesRegex(ValueError, "transaction state"):
                rollback_preflight(root, tx.name)

    def test_add_intended_plans_removal(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.setup_tx(root, "add")
            dest.write_bytes(b"new")
            result = rollback_preflight(root, tx.name)
            self.assertEqual(result["operations"][0]["action"], "remove_added")
            self.assertEqual(dest.read_bytes(), b"new")


if __name__ == "__main__":
    unittest.main()
