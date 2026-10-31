import base64
import contextlib
import copy
import hashlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
sys.path.insert(0, str(ROOT / "scripts"))
import verify_mcp_identity as verifier
from import_mcp_registry import API, OFFICIAL
from mcp_evidence import validate_evidence

TARBALL = b"package tarball"
TARBALL_URL = "https://registry.npmjs.org/@example/files/-/files-1.2.0.tgz"


def entry(**extra):
    data = {"id": "files", "name": "io.github.example/files", "description": "Read files", "version": "1.2.0",
            "repository": "https://github.com/example/files",
            "artifacts": [{"kind": "package", "registry": "npm", "identifier": "@example/files", "version": "1.2.0",
                           "transport": "stdio"}],
            "registry": {"status": "active", "published_at": "2026-09-01T10:00:00Z", "updated_at": "2026-10-01T10:00:00Z"},
            "level": "L0"}
    data.update(extra)
    return data


class FakeHttp:
    def __init__(self, **overrides):
        integrity = "sha512-" + base64.b64encode(hashlib.sha512(TARBALL).digest()).decode()
        self.responses = {
            f"{API}/servers/io.github.example%2Ffiles/versions/1.2.0": {
                "server": {"name": "io.github.example/files", "version": "1.2.0"}, "_meta": {OFFICIAL: {"status": "active"}}},
            f"{API}/servers/com.example%2Ffiles/versions/1.2.0": {
                "server": {"name": "com.example/files", "version": "1.2.0"}, "_meta": {OFFICIAL: {"status": "active"}}},
            "https://api.github.com/repos/example/files": {"owner": {"login": "example", "type": "Organization"},
                                                           "archived": False},
            "https://api.github.com/orgs/example": {"blog": "https://www.example.com"},
            "https://registry.npmjs.org/@example%2Ffiles/1.2.0": {
                "dist": {"tarball": TARBALL_URL, "integrity": integrity},
                "repository": {"type": "git", "url": "git+https://github.com/example/files.git"}},
            TARBALL_URL: TARBALL,
        }
        self.responses.update(overrides)

    def get(self, url, headers=None, limit=None):
        if url not in self.responses:
            raise urllib.error.HTTPError(url, 404, "not found", {}, None)
        body = self.responses[url]
        return (body if isinstance(body, bytes) else json.dumps(body).encode()), {}

    def json(self, url, headers=None):
        return json.loads(self.get(url)[0])


def results(evidence):
    return {c: evidence["identity"][c]["result"] for c in ("namespace", "repository", "artifacts")}


class IdentityTests(unittest.TestCase):
    def test_matching_owner_and_package_pass_and_pin_sha256(self):
        evidence = verifier.verify(entry(), FakeHttp())
        self.assertEqual(evidence["identity"]["result"], "pass", evidence["identity"])
        self.assertEqual(evidence["artifacts"][0]["sha256"], hashlib.sha256(TARBALL).hexdigest())

    def test_owner_mismatch_and_archived_repository_fail(self):
        http = FakeHttp(**{"https://api.github.com/repos/example/files": {"owner": {"login": "someone-else"}, "archived": False}})
        self.assertEqual(results(verifier.verify(entry(), http))["repository"], "fail")
        http = FakeHttp(**{"https://api.github.com/repos/example/files": {"owner": {"login": "example"}, "archived": True}})
        self.assertEqual(results(verifier.verify(entry(), http))["repository"], "fail")
        self.assertEqual(results(verifier.verify(entry(repository="https://github.com/missing/files"), FakeHttp()))["repository"], "fail")

    def test_domain_namespace_needs_the_organisation_website(self):
        domain_entry = entry(name="com.example/files")
        self.assertEqual(results(verifier.verify(domain_entry, FakeHttp()))["repository"], "pass")
        http = FakeHttp(**{"https://api.github.com/orgs/example": {"blog": "https://example.dev"}})
        self.assertEqual(results(verifier.verify(domain_entry, http))["repository"], "fail")
        hosted = entry(name="com.example/files", repository="https://git.example.com/team/files")
        self.assertEqual(results(verifier.verify(hosted, FakeHttp()))["repository"], "pass")
        self.assertEqual(verifier.namespace_domain("com.cloudflare.mcp/mcp"), "cloudflare.com")

    def test_unpublished_version_fails_namespace(self):
        self.assertEqual(results(verifier.verify(entry(version="9.9.9"), FakeHttp()))["namespace"], "fail")

    def test_tampered_or_unlinked_package_fails(self):
        self.assertEqual(results(verifier.verify(entry(), FakeHttp(**{TARBALL_URL: b"other bytes"})))["artifacts"], "fail")
        meta = FakeHttp().responses["https://registry.npmjs.org/@example%2Ffiles/1.2.0"]
        unlinked = dict(meta, repository={"url": "https://github.com/attacker/files"})
        http = FakeHttp(**{"https://registry.npmjs.org/@example%2Ffiles/1.2.0": unlinked})
        self.assertEqual(results(verifier.verify(entry(), http))["artifacts"], "fail")
        pinned = entry()
        pinned["artifacts"][0]["sha256"] = "c" * 64
        self.assertEqual(results(verifier.verify(pinned, FakeHttp()))["artifacts"], "fail")

    def test_mcpb_bundle_must_be_a_release_asset_with_the_registry_sha256(self):
        bundle, url = b"bundle", "https://github.com/example/files/releases/download/v1.2.0/files.mcpb"
        def bundle_entry(**artifact):
            data = {"kind": "package", "registry": "mcpb", "identifier": url, "version": "1.2.0", "transport": "stdio",
                    "sha256": hashlib.sha256(bundle).hexdigest()}
            return entry(artifacts=[dict(data, **artifact)])
        http = FakeHttp(**{url: bundle})
        self.assertEqual(results(verifier.verify(bundle_entry(), http))["artifacts"], "pass")
        self.assertEqual(results(verifier.verify(bundle_entry(sha256="0" * 64), http))["artifacts"], "fail")
        other = "https://example.com/files.mcpb"
        self.assertEqual(results(verifier.verify(bundle_entry(identifier=other), FakeHttp(**{other: bundle})))["artifacts"], "fail")
        unpinned = bundle_entry(); del unpinned["artifacts"][0]["sha256"]
        self.assertEqual(results(verifier.verify(unpinned, http))["artifacts"], "fail")

    def test_remote_only_server_has_nothing_to_pin(self):
        remote = entry(artifacts=[{"kind": "remote", "transport": "streamable-http", "url": "https://files.example.com/mcp"}])
        evidence = verifier.verify(remote, FakeHttp())
        self.assertEqual((evidence["identity"]["result"], evidence["artifacts"]), ("pass", []))

    def test_write_pins_catalog_and_evidence_without_raising_the_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            catalog = root / "mcp.json"
            catalog.write_text(json.dumps({"schema_version": 1, "source": "https://registry.modelcontextprotocol.io/v0.1",
                                           "servers": [entry()]}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = verifier.main(["files", "--write", "--catalog", str(catalog)], http=FakeHttp(), root=root)
            self.assertEqual(code, 0)
            written = json.loads(catalog.read_text(encoding="utf-8"))["servers"][0]
            self.assertEqual(written["level"], "L0")
            self.assertEqual(written["artifacts"][0]["sha256"], hashlib.sha256(TARBALL).hexdigest())
            evidence = json.loads((root / written["evidence"]).read_text(encoding="utf-8"))
            self.assertEqual(validate_evidence(evidence, written), "L1")

    def test_refuses_plain_http(self):
        with self.assertRaises(ValueError):
            verifier.Http().get("http://registry.npmjs.org/x")


if __name__ == "__main__":
    unittest.main()
