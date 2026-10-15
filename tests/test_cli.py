import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"

class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)

    def test_catalog_paths(self):
        for item in json.loads((ROOT / "registry/catalog.json").read_text())["items"]:
            self.assertTrue((ROOT / item["path"]).is_file())

    def test_list(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("code-review", result.stdout)

    def test_add_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_cli("add", "code-review", "--target", tmp).returncode, 0)
            self.assertNotEqual(self.run_cli("add", "code-review", "--target", tmp).returncode, 0)

if __name__ == "__main__":
    unittest.main()
