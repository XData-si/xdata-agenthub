"""XAH-304: reproduce hard-process termination after first file replacement.

POSIX-only test: monkeypatch os.replace inside a child process to call os._exit
after the first target replacement. This intentionally demonstrates a residual
crash-consistency gap; it is not a proof of safe automatic recovery.
"""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli"


@unittest.skipUnless(os.name == "posix", "Hard-exit crash rehearsal uses POSIX process semantics")
class InterruptedUpdateTests(unittest.TestCase):
    def test_hard_exit_leaves_lock_and_stale_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d)
            code = r"""
import os
import pathlib
import sys
sys.path.insert(0, sys.argv[1])
from installed_manifest import save_manifest, _digest
import update_apply
root = pathlib.Path(sys.argv[2])
a = root / "a.txt"
b = root / "b.txt"
src_a = root / "new-a.txt"
src_b = root / "new-b.txt"
a.write_bytes(b"old-a")
b.write_bytes(b"old-b")
src_a.write_bytes(b"new-a")
src_b.write_bytes(b"new-b")
save_manifest(root, {"schema_version": 1, "files": {
    "a.txt": {"sha256": _digest(a), "item_id": "test"},
    "b.txt": {"sha256": _digest(b), "item_id": "test"}}})
original_replace = update_apply.os.replace
def crash_after_first_replace(source, destination):
    result = original_replace(source, destination)
    if pathlib.Path(destination) == a:
        os._exit(73)
    return result
update_apply.os.replace = crash_after_first_replace
update_apply.apply_update(root, "test", [(src_a, a), (src_b, b)])
sys.exit(0)
"""
            child = subprocess.run([sys.executable, "-c", code, str(CLI), str(target)],
                                   capture_output=True, text=True, timeout=30)
            self.assertEqual(child.returncode, 73, child.stdout + child.stderr)
            self.assertEqual((target / "a.txt").read_bytes(), b"new-a")
            self.assertEqual((target / "b.txt").read_bytes(), b"old-b")
            self.assertTrue((target / ".xah-update.lock").is_dir())
            self.assertTrue((target / ".xah-update.lock" / "pid").is_file())
            self.assertTrue((target / ".xah-installed.json").is_file())
            from hashlib import sha256
            import json
            manifest = json.loads((target / ".xah-installed.json").read_text())
            self.assertEqual(manifest["files"]["a.txt"]["sha256"], sha256(b"old-a").hexdigest())
            # A second writer must fail closed, not overwrite partial state.
            retry = subprocess.run([sys.executable, str(CLI / "xah.py"),
                                    "update", "code-review", "--target", str(target),
                                    "--apply"], capture_output=True, text=True, timeout=30)
            self.assertNotEqual(retry.returncode, 0)
            self.assertIn("Update lock exists", retry.stderr)


if __name__ == "__main__":
    unittest.main()
