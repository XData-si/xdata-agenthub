import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from catalog_search import filter_items


class SearchFilterTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {"id": "b", "type": "skill", "description": "Code", "tags": ["security"],
             "targets": ["codex"], "license": "MIT", "source": "XData original"},
            {"id": "a", "type": "agent", "description": "Research", "targets": ["generic"],
             "license": "Apache-2.0", "source": "External reviewed"},
        ]

    def test_deterministic_and_composed_filters(self):
        self.assertEqual([x["id"] for x in filter_items(self.entries)], ["a", "b"])
        self.assertEqual([x["id"] for x in filter_items(self.entries, kind="skill",
            tag="SECURITY", agent="codex", license="mit", provenance="xdata")], ["b"])
        self.assertEqual(filter_items(self.entries, kind="skill", tag="missing"), [])

    def test_invalid_query_and_missing_tags(self):
        with self.assertRaises(ValueError):
            filter_items(self.entries, query="bad\x00query")
        self.assertEqual(filter_items(self.entries, tag="security", agent="generic"), [])

    def test_cli_json_and_empty_result(self):
        def run(*args):
            p = subprocess.run([sys.executable, str(ROOT / "cli/xah.py"), "search", *args],
                               cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        data = run("--kind", "skill", "--agent", "codex", "--json")
        self.assertTrue(data)
        self.assertTrue(all(x["type"] == "skill" and "codex" in x["targets"] for x in data))
        self.assertEqual(run("no-such-query-xyz", "--json"), [])


if __name__ == "__main__":
    unittest.main()
