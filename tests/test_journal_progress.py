import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from recovery_journal import transition_journal


class JournalProgressTests(unittest.TestCase):
    def test_progress_and_commit(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src = root / "source"
            src.write_bytes(b"new")
            tx = prepare_journal(root, "test", [("add", src, root / "dest")])
            transition_journal(tx, "applying")
            transition_journal(tx, "applying", completed=0)
            data = transition_journal(tx, "committed")
            self.assertTrue(data["operations"][0]["completed"])
            self.assertEqual(json.loads((tx / "journal.json").read_text())["state"], "committed")

    def test_refuses_commit_with_incomplete_operations(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src = root / "source"
            src.write_bytes(b"new")
            tx = prepare_journal(root, "test", [("add", src, root / "dest")])
            transition_journal(tx, "applying")
            with self.assertRaises(ValueError):
                transition_journal(tx, "committed")
            self.assertEqual(json.loads((tx / "journal.json").read_text())["state"], "applying")

    def test_refuses_illegal_transition(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src = root / "source"
            src.write_bytes(b"new")
            tx = prepare_journal(root, "test", [("add", src, root / "dest")])
            with self.assertRaises(ValueError):
                transition_journal(tx, "committed")


if __name__ == "__main__":
    unittest.main()
