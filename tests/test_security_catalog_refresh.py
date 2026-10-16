"""XAH-304 SEC-04/05: adversarial catalog-refresh inputs, no network calls."""
import hashlib
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from catalog_refresh import refresh_catalog


class FakeResponse:
    def __init__(self, payload, url):
        self.payload, self.url = payload, url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, count):
        return self.payload[:count]

    def geturl(self):
        return self.url


class CatalogRefreshSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.destination = pathlib.Path(self.temp.name) / "catalog.json"
        self.destination.write_bytes(b"original")
        self.url = "https://catalog.example/revisions/abc123/catalog.json"
        self.payload = b'{"schema_version":1,"items":[]}'
        self.digest = hashlib.sha256(self.payload).hexdigest()

    def refresh(self, **overrides):
        args = dict(source_url=self.url, revision="abc123",
                    sha256=self.digest, approve=True)
        args.update(overrides)
        return refresh_catalog(self.destination, **args)

    def test_refuse_untrusted_url_forms_before_network(self):
        urls = (
            "http://catalog.example/revisions/abc123/catalog.json",
            "file:///tmp/abc123/catalog.json",
            "https://user:password@catalog.example/abc123/catalog.json",
            "https://catalog.example/abc123/catalog.json#fragment",
            "https://catalog.example/revisions/not-pinned/catalog.json",
        )
        with patch("catalog_refresh.urlopen") as network:
            for url in urls:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    self.refresh(source_url=url)
            network.assert_not_called()
        self.assertEqual(self.destination.read_bytes(), b"original")

    def test_reject_oversize_payload_without_writing(self):
        oversize = b"x" * 2_000_001
        with patch("catalog_refresh.urlopen", return_value=FakeResponse(oversize, self.url)):
            with self.assertRaisesRegex(ValueError, "2 MB"):
                self.refresh(sha256=hashlib.sha256(oversize).hexdigest())
        self.assertEqual(self.destination.read_bytes(), b"original")

    def test_reject_symlinked_destination_before_network(self):
        real = pathlib.Path(self.temp.name) / "real.json"
        real.write_bytes(b"protected")
        self.destination.unlink()
        try:
            self.destination.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable on this platform")
        with patch("catalog_refresh.urlopen") as network:
            with self.assertRaises(ValueError):
                self.refresh()
            network.assert_not_called()
        self.assertEqual(real.read_bytes(), b"protected")

    def test_reject_nonexistent_destination_before_network(self):
        self.destination.unlink()
        with patch("catalog_refresh.urlopen") as network:
            with self.assertRaises(ValueError):
                self.refresh()
            network.assert_not_called()

    def test_reject_invalid_sha256_without_network(self):
        with patch("catalog_refresh.urlopen") as network:
            for sha in ("A" * 64, "z" * 64, "a" * 63, ""):
                with self.subTest(sha=sha), self.assertRaises(ValueError):
                    self.refresh(sha256=sha)
            network.assert_not_called()

    def test_refuse_redirect_and_preserve_catalog(self):
        with patch("catalog_refresh.urlopen",
                   return_value=FakeResponse(self.payload, "https://other.example/abc123/catalog.json")):
            with self.assertRaisesRegex(ValueError, "Redirects refused"):
                self.refresh()
        self.assertEqual(self.destination.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
