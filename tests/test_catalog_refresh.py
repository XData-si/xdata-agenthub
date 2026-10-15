import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from catalog_refresh import refresh_catalog


class Response:
    def __init__(self, payload, url):
        self.payload, self.url = payload, url
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, n):
        return self.payload[:n]
    def geturl(self):
        return self.url


class CatalogRefreshTests(unittest.TestCase):
    def test_opt_in_checksum_schema_and_offline_preserve_original(self):
        with tempfile.TemporaryDirectory() as d:
            dest = pathlib.Path(d) / "catalog.json"
            dest.write_bytes(b"original")
            payload = json.dumps({"schema_version": 1, "items": []}).encode()
            digest = hashlib.sha256(payload).hexdigest()
            url = "https://example.org/revisions/commit123/catalog.json"
            kwargs = dict(source_url=url, revision="commit123", sha256=digest)
            with self.assertRaises(ValueError):
                refresh_catalog(dest, **kwargs)
            with self.assertRaises(ValueError):
                refresh_catalog(dest, approve=True, offline=True, **kwargs)
            self.assertEqual(dest.read_bytes(), b"original")
            with patch("catalog_refresh.urlopen", return_value=Response(payload, url)):
                with self.assertRaises(ValueError):
                    refresh_catalog(dest, approve=True, **{**kwargs, "sha256": "0" * 64})
            self.assertEqual(dest.read_bytes(), b"original")
            with patch("catalog_refresh.urlopen", return_value=Response(b"invalid json", url)):
                with self.assertRaises(ValueError):
                    refresh_catalog(dest, approve=True, **{**kwargs, "sha256": hashlib.sha256(b"invalid json").hexdigest()})
            self.assertEqual(dest.read_bytes(), b"original")
            with patch("catalog_refresh.urlopen", return_value=Response(payload, url)):
                self.assertEqual(refresh_catalog(dest, approve=True, **kwargs), digest)
            self.assertEqual(dest.read_bytes(), payload)

    def test_reject_redirect_and_unpinned_url(self):
        with tempfile.TemporaryDirectory() as d:
            dest = pathlib.Path(d) / "catalog.json"
            dest.write_bytes(b"original")
            payload = b"{}"
            digest = hashlib.sha256(payload).hexdigest()
            url = "https://example.org/rev/abc/catalog.json"
            with self.assertRaises(ValueError):
                refresh_catalog(dest, source_url=url, revision="other", sha256=digest, approve=True)
            with patch("catalog_refresh.urlopen", return_value=Response(payload, "https://evil.example/catalog.json")):
                with self.assertRaises(ValueError):
                    refresh_catalog(dest, source_url=url, revision="abc", sha256=digest, approve=True)
            self.assertEqual(dest.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
