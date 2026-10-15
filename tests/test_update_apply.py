import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from installed_manifest import load_manifest, _digest
from update_apply import apply_update


class RollbackTests(unittest.TestCase):
    def test_failure_restores_original_bytes_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            a, b = root / "a.txt", root / "b.txt"
            a.write_bytes(b"old a")
            b.write_bytes(b"old b")
            src_a, src_b = root / "new-a", root / "new-b"
            src_a.write_bytes(b"new a")
            src_b.write_bytes(b"new b")
            from installed_manifest import save_manifest
            save_manifest(root, {"schema_version": 1, "files": {
                "a.txt": {"sha256": _digest(a), "item_id": "test"},
                "b.txt": {"sha256": _digest(b), "item_id": "test"}}})
            manifest_before = (root / ".xah-installed.json").read_bytes()
            with self.assertRaises(RuntimeError):
                apply_update(root, "test", [(src_a, a), (src_b, b)], fail_after=2)
            self.assertEqual(a.read_bytes(), b"old a")
            self.assertEqual(b.read_bytes(), b"old b")
            self.assertEqual((root / ".xah-installed.json").read_bytes(), manifest_before)

    def test_conflict_never_overwrites_local_edit(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            dest = root / "tracked.txt"
            src = root / "source.txt"
            dest.write_text("local", encoding="utf-8")
            src.write_text("new", encoding="utf-8")
            with self.assertRaises(ValueError):
                apply_update(root, "test", [(src, dest)])
            self.assertEqual(dest.read_text(encoding="utf-8"), "local")

    def test_traversal_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src = root / "source"
            src.write_text("new")
            with self.assertRaises(ValueError):
                apply_update(root, "test", [(src, root / ".." / "escape")])
            external = root / "external"
            external.write_text("untouched")
            link = root / "link"
            try:
                link.symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink unavailable")
            with self.assertRaises(ValueError):
                apply_update(root, "test", [(src, link)])
            self.assertEqual(external.read_text(), "untouched")


if __name__ == "__main__":
    unittest.main()
