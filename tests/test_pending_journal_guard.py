import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_journal import transition_journal
from recovery_guard import require_no_pending_transactions


class PendingJournalGuardTests(unittest.TestCase):
    def make_tx(self, root):
        source = root / "source"
        source.write_bytes(b"new")
        return prepare_journal(root, "test", [("add", source, root / "dest")])

    def test_empty_store_allows_writes(self):
        with tempfile.TemporaryDirectory() as d:
            require_no_pending_transactions(pathlib.Path(d))

    def test_prepared_blocks_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            self.make_tx(root)
            with self.assertRaisesRegex(ValueError, "Unresolved XAH transaction"):
                require_no_pending_transactions(root)

    def test_applying_blocks_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx = self.make_tx(root)
            transition_journal(tx, "applying")
            with self.assertRaisesRegex(ValueError, "Unresolved XAH transaction"):
                require_no_pending_transactions(root)

    def test_recovery_required_blocks_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx = self.make_tx(root)
            transition_journal(tx, "recovery_required")
            with self.assertRaisesRegex(ValueError, "Unresolved XAH transaction"):
                require_no_pending_transactions(root)

    def test_committed_does_not_block_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx = self.make_tx(root)
            transition_journal(tx, "applying")
            transition_journal(tx, "applying", completed=0)
            transition_journal(tx, "committed")
            require_no_pending_transactions(root)


if __name__ == "__main__":
    unittest.main()
