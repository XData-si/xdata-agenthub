import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from catalog_trust import classify_provenance

class CatalogTrustTests(unittest.TestCase):
    def test_declared_metadata_is_not_verification(self):
        result = classify_provenance({"source": "https://example.org/repo", "license": "MIT"})
        self.assertEqual(result["trust"], "declared_only")
    def test_missing_license(self):
        self.assertEqual(classify_provenance({"source": "https://example.org"} )["reason"], "missing_license")
    def test_http_source(self):
        self.assertEqual(classify_provenance({"source": "http://example.org", "license": "MIT"})["reason"], "insecure_source")
    def test_bad_entry(self):
        with self.assertRaises(ValueError):
            classify_provenance([])

    def test_descriptive_source_is_only_declared(self):
        result = classify_provenance({"source": "XData original", "license": "MIT"})
        self.assertEqual(result["trust"], "declared_only")

    def test_insecure_upstream_requires_review(self):
        result = classify_provenance({"source": "XData original", "license": "MIT",
                                      "upstream": {"url": "http://example.org/code"}})
        self.assertEqual(result["reason"], "upstream_insecure_source")

    def test_scheme_relative_url_requires_review(self):
        result = classify_provenance({"source": "//example.org/code", "license": "MIT"})
        self.assertEqual(result["trust"], "review_required")

    def test_https_credentials_require_review(self):
        result = classify_provenance({"source": "https://user:pass@example.org/code", "license": "MIT"})
        self.assertEqual(result["reason"], "invalid_https_source")
