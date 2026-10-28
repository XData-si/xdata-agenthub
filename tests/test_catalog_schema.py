"""XAH-201 schema validation regression tests."""
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from catalog_schema import validate_catalog


class CatalogSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v1 = json.loads((ROOT / "registry/catalog.json").read_text(encoding="utf-8"))

    def test_real_v1(self):
        self.assertEqual(len(validate_catalog(self.v1)), 107)

    def test_minimal_v2(self):
        doc = copy.deepcopy(self.v1)
        doc["schema_version"] = 2
        self.assertEqual(len(validate_catalog(doc)), 107)

    def test_full_v2(self):
        doc = copy.deepcopy(self.v1)
        doc["schema_version"] = 2
        doc["catalog_id"] = "xdata-agenthub"
        item = doc["items"][0]
        item.update(version="1.0", digest={"algorithm": "sha256", "value": "a" * 64},
                    tags=["review", "security"], upstream={"url": "https://example.org"},
                    compatibility={"claude": {"status": "native-observed", "tested_version": "2.1"}})
        self.assertEqual(len(validate_catalog(doc)), 107)

    def test_invalid_documents(self):
        for mutate in (
            lambda d: d.update(schema_version=3),
            lambda d: d.update(schema_version=True),
            lambda d: d.update(items={}),
            lambda d: d["items"].append(copy.deepcopy(d["items"][0])),
            lambda d: d["items"][0].update(path="../escape"),
            lambda d: d["items"][0].update(path="skills//bad"),
            lambda d: d["items"][0].update(id="../bad"),
            lambda d: d["items"][0].update(targets=["claude", "claude"]),
            lambda d: d["items"][0].update(unknown="x"),
        ):
            doc = copy.deepcopy(self.v1)
            mutate(doc)
            with self.subTest(doc=repr(doc)[:100]):
                with self.assertRaises(ValueError):
                    validate_catalog(doc)

    def test_invalid_v2_fields(self):
        for changes in (
            {"digest": {"algorithm": "md5", "value": "a" * 64}},
            {"digest": {"algorithm": "sha256", "value": "xyz"}},
            {"tags": ["duplicate", "duplicate"]},
            {"tags": ["UPPER"]},
            {"compatibility": {"claude": {"status": "certified"}}},
            {"upstream": {"url": ""}},
            {"version": 5},
        ):
            doc = copy.deepcopy(self.v1)
            doc["schema_version"] = 2
            doc["items"][0].update(changes)
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    validate_catalog(doc)


if __name__ == "__main__":
    unittest.main()
