import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from catalog_browse import facets, page

ITEMS = [{"id": "b", "type": "skill", "license": "MIT", "tags": ["ai", "ai"]},
         {"id": "a", "type": "agent", "license": "MIT", "tags": ["ai"]}]

class CatalogBrowseTests(unittest.TestCase):
    def test_facets_deduplicate_tags_per_entry(self):
        self.assertEqual(facets(ITEMS)["tag"]["ai"], 2)
    def test_page_stable_sort(self):
        self.assertEqual(page(ITEMS, limit=1)["items"][0]["id"], "a")
    def test_reject_negative_offset(self):
        with self.assertRaises(ValueError):
            page(ITEMS, offset=-1)
    def test_reject_boolean_limit(self):
        with self.assertRaises(ValueError):
            page(ITEMS, limit=True)
