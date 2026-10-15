import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from inspect_metadata import inspect_metadata
from installed_manifest import save_manifest


class InspectTests(unittest.TestCase):
    def test_declared_vs_verified_and_installed_states(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            src = root / "source"
            src.write_bytes(b"source bytes")
            digest = hashlib.sha256(src.read_bytes()).hexdigest()
            item = {"id": "sample", "type": "skill", "name": "Sample",
                    "source": "claimed", "license": "MIT", "targets": ["codex"],
                    "digest": {"algorithm": "sha256", "value": digest},
                    "compatibility": {"codex": {"status": "untested"}}}
            installed = root / "installed.md"
            installed.write_bytes(b"original")
            save_manifest(root, {"schema_version": 1, "files": {
                "installed.md": {"sha256": hashlib.sha256(b"original").hexdigest(), "item_id": "sample"}}})
            meta = inspect_metadata(item, src, root)
            self.assertTrue(meta["digest_matches"])
            self.assertEqual(meta["local_sha256"]["verification"], "computed-from-local-file")
            self.assertEqual(meta["source"]["verification"], "catalog-declared")
            self.assertEqual(meta["installed_files"][0]["state"], "untouched")
            installed.write_bytes(b"changed")
            self.assertEqual(inspect_metadata(item, src, root)["installed_files"][0]["state"], "modified")
            installed.unlink()
            self.assertEqual(inspect_metadata(item, src, root)["installed_files"][0]["state"], "missing")
            item["digest"]["value"] = "0" * 64
            self.assertFalse(inspect_metadata(item, src)["digest_matches"])

    def test_cli_json(self):
        p = subprocess.run([sys.executable, str(ROOT / "cli/xah.py"), "inspect",
                            "code-review", "--json"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["id"], "code-review")
        self.assertEqual(data["source"]["verification"], "catalog-declared")
        self.assertEqual(len(data["local_sha256"]["value"]), 64)


if __name__ == "__main__":
    unittest.main()
