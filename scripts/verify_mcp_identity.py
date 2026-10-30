#!/usr/bin/env python3
"""Verified MCP level L1: check identity and pin artifacts of catalog entries (standard library only).

For each entry, three checks (docs/VERIFIED_MCP.md, "Phase 2: L1 and L2 criteria"):
- namespace: the official registry lists this exact version as active;
- repository: the source repository exists, is not archived and belongs to the namespace owner;
- artifacts: every package is downloaded or resolved, its sha256 recorded, and it links back to the repository.

Nothing is installed or executed. With --write, package sha256 values are written to registry/mcp-servers.json and an
evidence document to reports/mcp/<id>/<version>.json; the catalog level is never changed (raising it is a reviewed
pull request). Set GITHUB_TOKEN to avoid GitHub API rate limits.

  python3 scripts/verify_mcp_identity.py playwright sentry      # print results
  python3 scripts/verify_mcp_identity.py --all --write
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
sys.path.insert(0, str(ROOT / "scripts"))
import mcp_catalog
import mcp_evidence
from import_mcp_registry import API, CATALOG, OFFICIAL, dump

MAX_BYTES = 200 * 1024 * 1024
OCI_ACCEPT = ", ".join(["application/vnd.oci.image.index.v1+json",
                        "application/vnd.docker.distribution.manifest.list.v2+json",
                        "application/vnd.oci.image.manifest.v1+json",
                        "application/vnd.docker.distribution.manifest.v2+json"])


class Http:
    """Small HTTPS client; tests replace it with a fake that serves canned responses."""

    def get(self, url, headers=None, limit=2 * 1024 * 1024):
        if not url.startswith("https://"):
            raise ValueError(f"refusing non-https URL {url}")
        request = urllib.request.Request(url, headers={"User-Agent": "xdata-agenthub", **(headers or {})})
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read(limit + 1)
            if len(body) > limit:
                raise ValueError(f"response from {url} is larger than {limit} bytes")
            return body, {k.lower(): v for k, v in response.headers.items()}

    def json(self, url, headers=None):
        return json.loads(self.get(url, {"Accept": "application/json", **(headers or {})})[0])


def _check(ok, details):
    return {"result": "pass" if ok else "fail", "details": details[:2000]}


def _github_headers():
    token = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def namespace_domain(name):
    """Registrable domain of a reverse-DNS namespace (com.cloudflare.mcp/x -> cloudflare.com); None for io.github.*."""
    namespace = name.split("/", 1)[0].lower()
    if namespace.startswith("io.github."):
        return None
    labels = namespace.split(".")
    return f"{labels[1]}.{labels[0]}" if len(labels) >= 2 else None


def repo_path(url):
    """(host, owner, repository) of an https repository URL."""
    parsed = urllib.parse.urlparse(re.sub(r"^git\+", "", url or ""))
    parts = [p for p in parsed.path.split("/") if p]
    if parsed.scheme not in ("https", "ssh", "git") or len(parts) < 2:
        return None
    return parsed.hostname.lower(), parts[0], parts[1].removesuffix(".git")


def same_repo(a, b):
    pa, pb = repo_path(a), repo_path(b)
    return bool(pa and pb) and tuple(x.lower() for x in pa) == tuple(x.lower() for x in pb)


def check_namespace(entry, http):
    url = f"{API}/servers/{urllib.parse.quote(entry['name'], safe='')}/versions/{urllib.parse.quote(entry['version'], safe='')}"
    try:
        record = http.json(url)
    except urllib.error.HTTPError as error:
        return _check(False, f"official registry: HTTP {error.code} for {entry['name']} {entry['version']}"), None
    status = record.get("_meta", {}).get(OFFICIAL, {}).get("status")
    server = record.get("server", {})
    ok = server.get("name") == entry["name"] and server.get("version") == entry["version"] and status == "active"
    return _check(ok, f"official registry lists {server.get('name')} {server.get('version')} as {status}"), record


def check_repository(entry, http):
    url = entry.get("repository")
    path = repo_path(url)
    if not path:
        return _check(False, "no source repository declared"), None
    host, owner, name = path
    domain = namespace_domain(entry["name"])
    if host == "github.com":
        try:
            repo = http.json(f"https://api.github.com/repos/{owner}/{name}", _github_headers())
        except urllib.error.HTTPError as error:
            return _check(False, f"GitHub repository {owner}/{name}: HTTP {error.code}"), None
        if repo.get("archived"):
            return _check(False, f"{owner}/{name} is archived"), repo
        actual = repo["owner"]["login"]
        if domain is None:
            expected = entry["name"].split("/", 1)[0][len("io.github."):]
            ok = actual.lower() == expected.lower()
            return _check(ok, f"namespace io.github.{expected}, repository owner {actual}"), repo
        site = ""
        if repo["owner"].get("type") == "Organization":
            site = http.json(f"https://api.github.com/orgs/{actual}", _github_headers()).get("blog") or ""
        site_host = (urllib.parse.urlparse(site if "://" in site else f"https://{site}").hostname or "").lower()
        ok = site_host == domain or site_host.endswith("." + domain)
        return _check(ok, f"namespace domain {domain}, GitHub organisation {actual} website {site or '(none)'}"), repo
    if domain and (host == domain or host.endswith("." + domain)):
        return _check(True, f"repository hosted on the namespace domain {host}"), None
    return _check(False, f"cannot confirm owner of {url} for namespace {entry['name']}"), None


def _npm(artifact, http):
    meta = http.json(f"https://registry.npmjs.org/{urllib.parse.quote(artifact['identifier'], safe='@')}/"
                     f"{urllib.parse.quote(artifact['version'], safe='')}")
    tarball, _ = http.get(meta["dist"]["tarball"], limit=MAX_BYTES)
    algorithm, _, expected = meta["dist"]["integrity"].partition("-")
    if algorithm != "sha512" or base64.b64encode(hashlib.sha512(tarball).digest()).decode() != expected:
        raise ValueError("npm tarball does not match its published integrity")
    repository = meta.get("repository")
    return hashlib.sha256(tarball).hexdigest(), [repository.get("url") if isinstance(repository, dict) else repository]


def _pypi(artifact, http):
    meta = http.json(f"https://pypi.org/pypi/{urllib.parse.quote(artifact['identifier'])}/"
                     f"{urllib.parse.quote(artifact['version'], safe='')}/json")
    files = sorted(meta["urls"], key=lambda f: (f["packagetype"] != "bdist_wheel", "none-any" not in f["filename"]))
    if not files:
        raise ValueError("no files published for this version")
    data, _ = http.get(files[0]["url"], limit=MAX_BYTES)
    digest = hashlib.sha256(data).hexdigest()
    if digest != files[0]["digests"]["sha256"]:
        raise ValueError("PyPI file does not match its published sha256")
    return digest, list((meta["info"].get("project_urls") or {}).values()) + [meta["info"].get("home_page")]


def _oci(artifact, http):
    reference = artifact["identifier"]
    image, _, tag = reference.rpartition(":") if "@" not in reference else (reference, "", "")
    host, _, repository = image.partition("/")
    if host == "docker.io":
        repository = repository if "/" in repository else f"library/{repository}"
        token_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repository}:pull"
        base = "https://registry-1.docker.io"
    elif host == "ghcr.io":
        token_url, base = f"https://ghcr.io/token?scope=repository:{repository}:pull", "https://ghcr.io"
    else:
        raise ValueError(f"unsupported OCI registry {host}")
    auth = {"Authorization": f"Bearer {http.json(token_url)['token']}"}
    body, headers = http.get(f"{base}/v2/{repository}/manifests/{tag}", {**auth, "Accept": OCI_ACCEPT})
    digest = headers.get("docker-content-digest") or "sha256:" + hashlib.sha256(body).hexdigest()
    if digest != "sha256:" + hashlib.sha256(body).hexdigest():
        raise ValueError("manifest does not match its digest")
    manifest = json.loads(body)
    if "manifests" in manifest:
        first = next(m for m in manifest["manifests"] if m.get("platform", {}).get("os") != "unknown")
        manifest = json.loads(http.get(f"{base}/v2/{repository}/manifests/{first['digest']}", {**auth, "Accept": OCI_ACCEPT})[0])
    config = json.loads(http.get(f"{base}/v2/{repository}/blobs/{manifest['config']['digest']}", auth)[0])
    source = (config.get("config") or {}).get("Labels", {}).get("org.opencontainers.image.source")
    return digest.removeprefix("sha256:"), [source]


RESOLVERS = {"npm": _npm, "pypi": _pypi, "oci": _oci}


def check_artifacts(entry, http):
    packages = [a for a in entry["artifacts"] if a["kind"] == "package"]
    if not packages:
        return _check(True, "remote endpoints only; nothing to pin"), []
    pinned, problems = [], []
    for artifact in packages:
        label = f"{artifact['registry']} {artifact['identifier']} {artifact['version']}"
        resolver = RESOLVERS.get(artifact["registry"])
        if not resolver:
            problems.append(f"{label}: registry not supported by the verifier")
            continue
        try:
            digest, sources = resolver(artifact, http)
        except (ValueError, KeyError, StopIteration, urllib.error.URLError) as error:
            problems.append(f"{label}: {error}")
            continue
        if artifact.get("sha256") and artifact["sha256"] != digest:
            problems.append(f"{label}: sha256 changed from the pinned {artifact['sha256']}")
        if not any(same_repo(s, entry.get("repository")) for s in sources if s):
            problems.append(f"{label}: does not link to {entry.get('repository')} ({', '.join(filter(None, sources)) or 'no source'})"[:300])
        pinned.append({"registry": artifact["registry"], "identifier": artifact["identifier"],
                       "version": artifact["version"], "sha256": digest})
    details = "; ".join(problems) or "pinned: " + ", ".join(f"{p['identifier']} sha256:{p['sha256'][:12]}…" for p in pinned)
    return _check(not problems, details), pinned


def verify(entry, http, now=None):
    """Return an evidence document with the identity section for one catalog entry."""
    namespace, _ = check_namespace(entry, http)
    repository, _ = check_repository(entry, http)
    artifacts, pinned = check_artifacts(entry, http)
    passed = all(c["result"] == "pass" for c in (namespace, repository, artifacts))
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return {
        "schema_version": 1,
        "server": {"id": entry["id"], "name": entry["name"], "version": entry["version"]},
        "artifacts": pinned,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "identity": {"result": "pass" if passed else "fail", "tool": "verify_mcp_identity.py",
                     "namespace": namespace, "repository": repository, "artifacts": artifacts},
    }


def apply(catalog, entry_id, evidence, root):
    """Write pinned sha256 values into the catalog entry and the evidence document next to it; level is unchanged."""
    entry = next(e for e in catalog["servers"] if e["id"] == entry_id)
    digests = {(p["registry"], p["identifier"], p["version"]): p["sha256"] for p in evidence["artifacts"]}
    complete = all((a["registry"], a["identifier"], a["version"]) in digests
                   for a in entry["artifacts"] if a["kind"] == "package")
    if not complete:
        return None
    for artifact in entry["artifacts"]:
        if artifact["kind"] == "package":
            artifact["sha256"] = digests[(artifact["registry"], artifact["identifier"], artifact["version"])]
    relative = f"reports/mcp/{entry['id']}/{entry['version']}.json"
    entry["evidence"] = relative
    mcp_catalog.validate_entry(entry)
    mcp_evidence.validate_evidence(evidence, entry)
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return relative


def main(argv=None, http=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--catalog", default=str(CATALOG))
    args = parser.parse_args(argv)
    path = pathlib.Path(args.catalog)
    catalog = json.loads(path.read_text(encoding="utf-8"))
    servers = mcp_catalog.validate_mcp_catalog(catalog)
    ids = [s["id"] for s in servers] if args.all else args.ids
    unknown = sorted(set(ids) - {s["id"] for s in servers})
    if not ids or unknown:
        parser.error(f"unknown or missing ids: {', '.join(unknown) or '(none)'}")
    http = http or Http()
    failed = 0
    for entry_id in ids:
        entry = next(s for s in servers if s["id"] == entry_id)
        evidence = verify(entry, http)
        identity = evidence["identity"]
        failed += identity["result"] != "pass"
        print(f"{entry_id}: identity {identity['result']}")
        for check in mcp_evidence.IDENTITY_CHECKS:
            print(f"  {check:10} {identity[check]['result']}: {identity[check]['details']}")
        if args.write and (written := apply(catalog, entry_id, evidence, root)):
            print(f"  wrote {written}")
    if args.write:
        mcp_catalog.validate_mcp_catalog(catalog)
        path.write_text(dump(catalog), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
