#!/usr/bin/env python3
"""Verified MCP level L2: scan one catalog entry and write an evidence document (runs in CI, needs Docker).

Steps for every pinned package (docs/VERIFIED_MCP.md, "Phase 2: L1 and L2 criteria"):
1. L1 identity checks (scripts/verify_mcp_identity.py);
2. fetch the exact artifact and compare its sha256 with the pin (npm tarball, OCI image by digest);
3. start the server in a container without network, capabilities or credentials and read tools/list only;
4. SBOM (syft), known vulnerabilities (osv-scanner), secrets in the artifact (gitleaks), declared licence.

The evidence document is written to OUT/<id>/<version>.json together with the raw scanner reports. Nothing is
committed: a maintainer reviews the evidence and raises the level in a pull request. npm dependencies are installed
with --ignore-scripts, so no install script runs; the server process itself only runs inside the isolated container.

  python3 scripts/mcp_l2_scan.py playwright --out "$RUNNER_TEMP/mcp-evidence"
"""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
sys.path.insert(0, str(ROOT / "scripts"))
import mcp_catalog
import mcp_evidence
import mcp_tool_scan
import mcp_tools_list
import verify_mcp_identity
from import_mcp_registry import CATALOG

NODE_IMAGE = "docker.io/library/node:22-slim@sha256:4b150b48b4116e2a22f2c39cc27025fbf4f153e2078fd3b14d159fdb5c7279da"
ISOLATION = ["--rm", "-i", "--network", "none", "--read-only", "--tmpfs", "/tmp:rw,size=256m", "--cap-drop", "ALL",
             "--security-opt", "no-new-privileges", "--pids-limit", "256", "--memory", "1g"]
# OSI-approved licences seen in MCP servers; anything else fails and is reviewed by a person.
OSI_LICENCES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0", "0BSD", "Unlicense",
                "LGPL-2.1-only", "LGPL-3.0-only", "GPL-2.0-only", "GPL-3.0-only", "AGPL-3.0-only", "EPL-2.0",
                "LGPL-2.1-or-later", "LGPL-3.0-or-later", "GPL-2.0-or-later", "GPL-3.0-or-later", "AGPL-3.0-or-later"}
HIGH_SEVERITY = 7.0
# Reviewed per-server arguments for servers whose registry entry does not declare how to start them on stdio.
EXTRA_ARGS = json.loads((ROOT / "scripts" / "mcp_verify_args.json").read_text(encoding="utf-8"))["servers"]


def run(argv, timeout=900, **kwargs):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"{argv[0]} exited {result.returncode}: {(result.stderr or result.stdout)[-500:]}")
    return result.stdout


def tool_version(argv):
    try:
        return run(argv, timeout=60).strip().splitlines()[0][:80]
    except (OSError, RuntimeError, IndexError):
        return "unknown"


def server_args(entry, package_record):
    """Arguments after the image or executable: registry packageArguments plus reviewed extra arguments."""
    args = []
    for arg in (package_record or {}).get("packageArguments", []):
        value = arg.get("value") or arg.get("default")
        if value and "{" in value:
            continue  # needs user input; never guessed
        if arg.get("type") == "named":
            args += [arg["name"]] + ([value] if value else [])
        elif value:
            args.append(value)
    return args + EXTRA_ARGS.get(entry["id"], {}).get("args", [])


def placeholder_env(entry):
    """Required variables get inert placeholders: the container has no network, so nothing can use them."""
    env = {}
    for var in entry.get("environment", []):
        if var["required"]:
            name = var["name"]
            env[name] = "http://127.0.0.1:9" if name.endswith(("_URL", "_HOST", "_ENDPOINT")) else "xah-verifier-placeholder"
    return env


def npm_bin(package_json):
    """Path of the package's executable (package.json `bin`), relative to the package root."""
    binary = package_json.get("bin")
    if isinstance(binary, str):
        return binary
    if isinstance(binary, dict) and binary:
        short = package_json.get("name", "").rsplit("/", 1)[-1]
        return binary.get(short) or binary.get(package_json.get("name")) or sorted(binary.items())[0][1]
    raise ValueError("package.json has no bin entry")


def licence_result(declared, repository_spdx):
    declared = (declared or "").strip()
    if declared not in OSI_LICENCES:
        return {"result": "fail", "details": f"declared licence {declared or '(none)'} is not on the OSI allowlist"}
    if repository_spdx and repository_spdx not in ("NOASSERTION", declared):
        return {"result": "fail", "details": f"package declares {declared}, repository {repository_spdx}"}
    return {"result": "pass", "details": f"{declared}" + (f", matches repository" if repository_spdx == declared else "")}


def osv_result(report):
    """Fail on any known vulnerability with CVSS >= 7.0. Unscored advisories (common in the Go database) are listed
    for the reviewer but do not fail the scan on their own."""
    high, unscored, total = [], [], 0
    for result in report.get("results", []):
        for package in result.get("packages", []):
            name = f"{package['package'].get('name')}@{package['package'].get('version')}"
            for group in package.get("groups", []):
                total += 1
                label = f"{name} {','.join(group.get('ids', [])[:2])}"
                try:
                    severity = float(group.get("max_severity") or "")
                except ValueError:
                    unscored.append(label)
                    continue
                if severity >= HIGH_SEVERITY:
                    high.append(f"{label} ({group['max_severity']})")
    details = f"{total} known vulnerabilities, {len(high)} high/critical, {len(unscored)} unscored"
    if high:
        details += "; high/critical: " + "; ".join(high[:15])
    if unscored:
        details += "; unscored: " + "; ".join(unscored[:10])
    return {"result": "fail" if high else "pass", "details": details}


def gitleaks_result(findings, root=None):
    if findings:
        relative = lambda p: os.path.relpath(p, root) if root and os.path.isabs(p or "") else p
        where = sorted({f"{relative(f.get('File'))}:{f.get('StartLine')} ({f.get('RuleID')})" for f in findings})
        return {"result": "fail", "details": f"{len(findings)} possible secrets: " + "; ".join(where[:20])}
    return {"result": "pass", "details": "no secrets found"}


def sbom_result(sbom):
    components = len(sbom.get("components", []))
    return {"result": "pass" if components else "fail", "details": f"CycloneDX SBOM with {components} components"}


def combine(results):
    """One result per scan across all packages of a server: pass only if every package passed."""
    return {"result": "pass" if all(r["result"] == "pass" for r in results) else "fail",
            "details": " | ".join(r["details"] for r in results)[:2000]}


def safe_extract(archive, target):
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            path = (target / member.name).resolve()
            if not path.is_relative_to(target.resolve()) or member.issym() or member.islnk() or member.isdev():
                raise ValueError(f"unsafe path in package: {member.name}")
        tar.extractall(target, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))


def prepare_npm(artifact, entry, work, http, extra):
    meta = http.json(f"https://registry.npmjs.org/{urllib.parse.quote(artifact['identifier'], safe='@')}/"
                     f"{urllib.parse.quote(artifact['version'], safe='')}")
    tarball, _ = http.get(meta["dist"]["tarball"], limit=verify_mcp_identity.MAX_BYTES)
    if hashlib.sha256(tarball).hexdigest() != artifact["sha256"]:
        raise ValueError("npm tarball does not match the pinned sha256")
    archive = work / "package.tgz"
    archive.write_bytes(tarball)
    safe_extract(archive, work)
    package = work / "package"
    package_json = json.loads((package / "package.json").read_text(encoding="utf-8"))
    # Only production dependencies are installed; devDependencies may name unpublished workspace packages.
    install_json = {k: v for k, v in package_json.items() if k != "devDependencies"}
    (package / "package.json").write_text(json.dumps(install_json, indent=2), encoding="utf-8")
    run(["npm", "install", "--omit=dev", "--ignore-scripts", "--no-audit", "--no-fund", "--package-lock"], cwd=package)
    binary = npm_bin(package_json)
    env = [x for k, v in placeholder_env(entry).items() for x in ("-e", f"{k}={v}")]
    command = ["docker", "run", *ISOLATION, "--user", "65534:65534", "-v", f"{package}:/app:ro", "-w", "/app", *env,
               NODE_IMAGE, "node", f"/app/{binary}", *extra]
    return {"command": command, "sbom": f"dir:{package}", "osv": ["scan", "source", "--lockfile", str(package / "package-lock.json")],
            "secrets_dir": package, "secrets_exclude": ["node_modules"], "licence": package_json.get("license")}


def prepare_oci(artifact, entry, work, extra):
    image = artifact["identifier"].rsplit(":", 1)[0] if "@" not in artifact["identifier"] else artifact["identifier"].split("@")[0]
    reference = f"{image}@sha256:{artifact['sha256']}"
    run(["docker", "pull", "--quiet", reference])
    labels = json.loads(run(["docker", "image", "inspect", "--format", "{{json .Config.Labels}}", reference]) or "null") or {}
    container = run(["docker", "create", reference]).strip()
    rootfs = work / "rootfs"
    rootfs.mkdir()
    try:
        export = work / "rootfs.tar"
        run(["docker", "export", "--output", str(export), container])
        with tarfile.open(export) as tar:
            members = [m for m in tar.getmembers() if m.isfile() and not m.name.startswith(("proc/", "sys/", "dev/"))]
            tar.extractall(rootfs, members=members, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
        export.unlink()
    finally:
        run(["docker", "rm", container])
    env = [x for k, v in placeholder_env(entry).items() for x in ("-e", f"{k}={v}")]
    return {"command": ["docker", "run", *ISOLATION, *env, reference, *extra], "sbom": reference,
            "osv": ["scan", "image", reference], "secrets_dir": rootfs, "secrets_exclude": [],
            "licence": labels.get("org.opencontainers.image.licenses")}


def repository_spdx(entry, http):
    path = verify_mcp_identity.repo_path(entry.get("repository"))
    if not path or path[0] != "github.com":
        return None
    repo = http.json(f"https://api.github.com/repos/{path[1]}/{path[2]}", verify_mcp_identity._github_headers())
    return (repo.get("license") or {}).get("spdx_id")


def scan_package(artifact, entry, work, reports, http, record=None):
    package_record = next((p for p in ((record or {}).get("server") or {}).get("packages", [])
                           if p.get("registryType") == artifact["registry"] and p.get("identifier") == artifact["identifier"]), None)
    extra = server_args(entry, package_record)
    prepared = (prepare_npm(artifact, entry, work, http, extra) if artifact["registry"] == "npm"
                else prepare_oci(artifact, entry, work, extra) if artifact["registry"] == "oci"
                else None)
    if prepared is None:
        raise ValueError(f"{artifact['registry']} packages are not supported by the L2 scanner yet")
    stem = f"{artifact['registry']}-{hashlib.sha256(artifact['identifier'].encode()).hexdigest()[:8]}"
    listing = mcp_tools_list.list_tools(prepared["command"], timeout=120)
    (reports / f"{stem}-tools.json").write_text(json.dumps(listing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sbom_path = reports / f"{stem}-sbom.cdx.json"
    run(["syft", "scan", prepared["sbom"], "--quiet", "-o", f"cyclonedx-json={sbom_path}"])
    osv_path = reports / f"{stem}-osv.json"
    osv = subprocess.run(["osv-scanner", *prepared["osv"], "--format", "json", "--output", str(osv_path)],
                         capture_output=True, text=True, timeout=900)
    if osv.returncode not in (0, 1):  # 1 = vulnerabilities found
        raise RuntimeError(f"osv-scanner exited {osv.returncode}: {osv.stderr[-500:]}")
    secrets_path = reports / f"{stem}-gitleaks.json"
    with tempfile.TemporaryDirectory() as config_dir:
        config = pathlib.Path(config_dir) / "gitleaks.toml"
        text = "[extend]\nuseDefault = true\n"
        if prepared["secrets_exclude"]:
            paths = "".join(f"  '''(^|/){p}/''',\n" for p in prepared["secrets_exclude"])
            text += f"\n[allowlist]\npaths = [\n{paths}]\n"
        config.write_text(text, encoding="utf-8")
        run(["gitleaks", "dir", str(prepared["secrets_dir"]), "--config", str(config), "--no-banner",
             "--report-format", "json", "--report-path", str(secrets_path), "--exit-code", "0", "--redact"])
    return {
        "args": extra,
        "tools": listing["tools"],
        "sbom": sbom_result(json.loads(sbom_path.read_text(encoding="utf-8"))),
        "dependencies": osv_result(json.loads(osv_path.read_text(encoding="utf-8") or "{}")),
        "secrets": gitleaks_result(json.loads(secrets_path.read_text(encoding="utf-8") or "[]"), str(prepared["secrets_dir"])),
        "licence": licence_result(prepared["licence"], repository_spdx(entry, http)),
    }


def assemble(evidence, entry, per_package, versions):
    """Add the L2 sections to an identity evidence document; returns (evidence, supported level)."""
    tools = per_package[0]["tools"] if per_package else []
    findings = mcp_tool_scan.scan_tools(tools)
    errors = sum(1 for f in findings if f[1] == "error")
    shown = "; ".join(f"{f[0]} {f[2]}.{f[3]}: {f[4]}" for f in findings if f[1] == "error")[:1500]
    differing = [i for i, p in enumerate(per_package) if mcp_tool_scan.tools_digest(p["tools"]) != mcp_tool_scan.tools_digest(tools)]
    tools_ok = bool(tools) and not errors and not differing
    details = f"{len(tools)} tools, {errors} errors, {len(findings) - errors} warnings" + (f": {shown}" if shown else "")
    if differing:
        details += "; packages expose different tools"
    started = sorted({" ".join(p.get("args", [])) for p in per_package} - {""})
    if started:
        details += "; started with arguments: " + " / ".join(started)
    scans = {"tools": {"result": "pass" if tools_ok else "fail", "tool": "mcp_tool_scan.py", "details": details,
                       "count": len(tools), "digest": mcp_tool_scan.tools_digest(tools), "errors": errors,
                       "warnings": len(findings) - errors}}
    for scan, tool in (("dependencies", "osv"), ("sbom", "syft"), ("secrets", "gitleaks"), ("licence", None)):
        scans[scan] = combine([p[scan] for p in per_package]) if per_package else {"result": "fail", "details": "not scanned"}
        if tool:
            scans[scan]["tool"] = versions[tool]
    evidence = dict(evidence, scans=scans, tools=tools)
    return evidence, mcp_evidence.validate_evidence(evidence, entry)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("id")
    parser.add_argument("--out", required=True)
    parser.add_argument("--catalog", default=str(CATALOG))
    parser.add_argument("--run-url")
    args = parser.parse_args(argv)
    catalog = json.loads(pathlib.Path(args.catalog).read_text(encoding="utf-8"))
    servers = mcp_catalog.validate_mcp_catalog(catalog)
    entry = next((s for s in servers if s["id"] == args.id), None)
    if entry is None:
        parser.error(f"unknown id {args.id}")
    http = verify_mcp_identity.Http()
    evidence = verify_mcp_identity.verify(entry, http)
    _, record = verify_mcp_identity.check_namespace(entry, http)
    if args.run_url:
        evidence["run"] = args.run_url
    # Scan exactly what the identity step pinned; a catalog pin that differs already failed identity.
    pins = {(p["registry"], p["identifier"], p["version"]): p["sha256"] for p in evidence["artifacts"]}
    entry = json.loads(json.dumps(entry))
    for artifact in entry["artifacts"]:
        if artifact["kind"] == "package" and (key := (artifact["registry"], artifact["identifier"], artifact["version"])) in pins:
            artifact["sha256"] = pins[key]
    out = pathlib.Path(args.out) / entry["id"]
    reports = out / entry["version"]
    reports.mkdir(parents=True, exist_ok=True)
    versions = {"syft": tool_version(["syft", "version"]).replace("Application:", "syft").strip(),
                "osv": tool_version(["osv-scanner", "--version"]), "gitleaks": "gitleaks " + tool_version(["gitleaks", "version"])}
    per_package, problems = [], []
    packages = [a for a in entry["artifacts"] if a["kind"] == "package"]
    if len(pins) == len(packages):
        for artifact in packages:
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    per_package.append(scan_package(artifact, entry, pathlib.Path(tmp), reports, http, record))
                except (OSError, RuntimeError, ValueError, mcp_tools_list.McpError, subprocess.TimeoutExpired) as error:
                    problems.append(f"{artifact['identifier']}: {error}")
    if packages and len(per_package) == len(packages):
        evidence, level = assemble(evidence, entry, per_package, versions)
    elif problems or len(pins) != len(packages):
        level = "L0"
    else:
        level = mcp_evidence.validate_evidence(evidence, entry)
    path = out / f"{entry['version']}.json"
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{entry['id']} {entry['version']}: evidence supports {level}")
    for check in mcp_evidence.IDENTITY_CHECKS:
        print(f"  identity.{check}: {evidence['identity'][check]['result']} - {evidence['identity'][check]['details']}")
    for scan, result in evidence.get("scans", {}).items():
        print(f"  {scan}: {result['result']} - {result['details'][:300]}")
    for problem in problems:
        print(f"  error: {problem}"[:600])
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
