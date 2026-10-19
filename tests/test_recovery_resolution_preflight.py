import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from journal_prepare import prepare_journal
from installed_manifest import save_manifest, _digest
from recovery_journal import transition_journal
from recovery_resolution_preflight import resolution_preflight


class ResolutionPreflightTests(unittest.TestCase):
    def fixture(self, root):
        src, dest = root / "src", root / "dest"
        src.write_bytes(b"new")
        dest.write_bytes(b"old")
        save_manifest(root, {"schema_version": 1, "files": {
            "dest": {"sha256": _digest(dest), "item_id": "test"}}})
        tx = prepare_journal(root, "test", [("update", src, dest)])
        transition_journal(tx, "recovery_required")
        return tx, dest

    def test_original_file_passes_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            result = resolution_preflight(root, tx.name)
            self.assertTrue(result["files_restored"])
            self.assertTrue(result["manifest_verified"])
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

    def test_manifest_digest_mismatch_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            save_manifest(root, {"schema_version": 1, "files": {
                "dest": {"sha256": "0" * 64, "item_id": "test"}}})
            with self.assertRaisesRegex(ValueError, "Manifest checksum"):
                resolution_preflight(root, tx.name)

    def test_manifest_ownership_mismatch_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            tx, dest = self.fixture(root)
            save_manifest(root, {"schema_version": 1, "files": {
                "dest": {"sha256": _digest(dest), "item_id": "other"}}})
            with self.assertRaisesRegex(ValueError, "Manifest ownership"):
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
