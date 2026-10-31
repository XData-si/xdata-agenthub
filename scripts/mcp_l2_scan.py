#!/usr/bin/env python3
"""Verified MCP level L2: scan one catalog entry and write an evidence document (runs in CI, needs Docker).

Steps for every pinned package (docs/VERIFIED_MCP.md, "Phase 2: L1 and L2 criteria"):
1. L1 identity checks (scripts/verify_mcp_identity.py);
2. fetch the exact artifact and compare its sha256 with the pin (npm tarball, PyPI wheel, MCP bundle, OCI image by
   digest);
3. start the server in a container without network, capabilities or credentials and read tools/list only;
4. SBOM (syft), known vulnerabilities (osv-scanner), secrets in the artifact (gitleaks), declared licence.

The evidence document is written to OUT/<id>/<version>.json together with the raw scanner reports. Nothing is
committed: a maintainer reviews the evidence and raises the level in a pull request. npm dependencies are installed
with --ignore-scripts and PyPI dependencies as wheels only (--only-binary), so no install or build script runs; the
server process itself only runs inside the isolated container.

  python3 scripts/mcp_l2_scan.py playwright --out "$RUNNER_TEMP/mcp-evidence"
"""
import argparse
import hashlib
import json
import os
import pathlib
import posixpath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import zipfile

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
# Same minor version as the workflow's setup-python, which installs the wheels the container then imports.
PYTHON_IMAGE = "docker.io/library/python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159"
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
        # A fixed value is passed as declared; a required argument also with its default. An optional argument
        # without a value is an option the user may set (some servers list every option), so it is left out.
        value = arg.get("value") or (arg.get("default") if arg.get("isRequired") else None)
        if not value or "{" in value:
            continue  # absent, or needs user input; never guessed
        if arg.get("type") == "named":
            args += [arg["name"], value]
        else:
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


class NotScannable(Exception):
    """The artifact is valid but this scanner cannot run it (for example a Python MCP bundle); no L2, identity stands."""


def wheel_console_script(entry_points, preferred):
    """`module:attr` of the console script in a wheel's entry_points.txt, preferring the given names."""
    scripts, section = {}, None
    for line in entry_points.splitlines():
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]").strip()
        elif section == "console_scripts" and "=" in line:
            name, _, target = line.partition("=")
            scripts[name.strip()] = target.split("[")[0].strip()
    if not scripts:
        raise ValueError("the wheel declares no console script")
    for name in preferred:
        if name in scripts:
            return scripts[name]
    return scripts[sorted(scripts)[0]]


def python_launcher(target):
    """`python -c` code that calls a console-script target such as `pkg.cli:main`."""
    module, _, attr = target.partition(":")
    if not all(part.isidentifier() for part in module.split(".") + (attr.split(".") if attr else [])):
        raise ValueError(f"unexpected console script target {target!r}")
    call = "".join(f".{part}" for part in attr.split(".")) if attr else ""
    return f"import sys, importlib; sys.argv[0] = {module!r}; sys.exit(importlib.import_module({module!r}){call}())"


PYPI_LICENCE_CLASSIFIERS = {"License :: OSI Approved :: MIT License": "MIT",
                            "License :: OSI Approved :: Apache Software License": "Apache-2.0",
                            "License :: OSI Approved :: ISC License (ISCL)": "ISC",
                            "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0"}


def pypi_licence(info):
    """SPDX licence of a PyPI release: License-Expression, else an SPDX License field, else a known classifier."""
    for value in (info.get("license_expression"), info.get("license")):
        if value and value.strip() in OSI_LICENCES:
            return value.strip()
    found = {PYPI_LICENCE_CLASSIFIERS[c] for c in info.get("classifiers", []) if c in PYPI_LICENCE_CLASSIFIERS}
    return found.pop() if len(found) == 1 else (info.get("license_expression") or info.get("license"))


def installed_requirements(site):
    """`name==version` for every distribution installed into a --target directory (input for osv-scanner)."""
    lines = []
    for metadata in sorted(pathlib.Path(site).glob("*.dist-info/METADATA")):
        fields = dict(line.split(": ", 1) for line in metadata.read_text(encoding="utf-8", errors="replace")
                      .split("\n\n", 1)[0].splitlines() if ": " in line)
        if fields.get("Name") and fields.get("Version"):
            lines.append(f"{fields['Name']}=={fields['Version']}")
    return "\n".join(lines) + "\n"


def mcpb_entry_point(manifest):
    """Entry point of a Node MCP bundle (manifest.json `server`), relative to the bundle root."""
    server = manifest.get("server") or {}
    if server.get("type") != "node":
        raise NotScannable(f"MCP bundles of type {server.get('type')!r} are not supported by the L2 scanner yet")
    entry_point = server.get("entry_point") or ""
    if not entry_point or posixpath.isabs(entry_point) or ".." in entry_point.split("/"):
        raise ValueError(f"unsafe or missing entry_point {entry_point!r}")
    return entry_point


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
        # gitleaks reports POSIX paths (the scan runs on Linux), also when these tests run on Windows.
        relative = lambda p: posixpath.relpath(p, root) if root and posixpath.isabs(p or "") else p
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


def safe_extract_zip(archive, target):
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            path = (target / info.filename).resolve()
            mode = info.external_attr >> 16
            if not path.is_relative_to(target.resolve()) or (mode & 0o170000) == 0o120000:
                raise ValueError(f"unsafe path in archive: {info.filename}")
        bundle.extractall(target)


def node_command(entry, package, script, extra):
    env = [x for k, v in placeholder_env(entry).items() for x in ("-e", f"{k}={v}")]
    # nobody (65534) has no home directory; servers that write a config or cache there get the writable /tmp.
    return ["docker", "run", *ISOLATION, "--user", "65534:65534", "-e", "HOME=/tmp", "-v", f"{package}:/app:ro",
            "-w", "/app", *env, NODE_IMAGE, "node", f"/app/{script}", *extra]


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
    command = node_command(entry, package, npm_bin(package_json), extra)
    return {"command": command, "sbom": f"dir:{package}", "osv": ["scan", "source", "--lockfile", str(package / "package-lock.json")],
            "secrets_dir": package, "secrets_exclude": ["node_modules"], "licence": package_json.get("license")}


def prepare_pypi(artifact, entry, work, http, extra):
    meta = http.json(f"https://pypi.org/pypi/{urllib.parse.quote(artifact['identifier'])}/"
                     f"{urllib.parse.quote(artifact['version'], safe='')}/json")
    file = next((f for f in meta["urls"] if f["digests"]["sha256"] == artifact["sha256"]), None)
    if file is None:
        raise ValueError("no PyPI file matches the pinned sha256")
    if file["packagetype"] != "bdist_wheel":
        raise NotScannable("only wheels are scanned; an sdist would run its build code")
    data, _ = http.get(file["url"], limit=verify_mcp_identity.MAX_BYTES)
    if hashlib.sha256(data).hexdigest() != artifact["sha256"]:
        raise ValueError("PyPI file does not match the pinned sha256")
    wheel = work / file["filename"]
    wheel.write_bytes(data)
    unpacked, site = work / "wheel", work / "site"
    unpacked.mkdir()
    safe_extract_zip(wheel, unpacked)
    # Dependencies as wheels only: installing a wheel copies files, no build or install script runs.
    run([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-compile",
         "--only-binary=:all:", "--target", str(site), str(wheel)])
    entry_points = next(unpacked.glob("*.dist-info/entry_points.txt"), None)
    if entry_points is None:
        raise ValueError("the wheel declares no console script")
    names = [artifact["identifier"], artifact["identifier"].replace("_", "-")]
    code = python_launcher(wheel_console_script(entry_points.read_text(encoding="utf-8"), names))
    (work / "requirements.txt").write_text(installed_requirements(site), encoding="utf-8")
    env = [x for k, v in placeholder_env(entry).items() for x in ("-e", f"{k}={v}")]
    command = ["docker", "run", *ISOLATION, "--user", "65534:65534", "-e", "HOME=/tmp", "-e", "PYTHONPATH=/app",
               "-e", "PYTHONDONTWRITEBYTECODE=1", "-v", f"{site}:/app:ro", "-w", "/tmp", *env, PYTHON_IMAGE,
               "python", "-c", code, *extra]
    return {"command": command, "sbom": f"dir:{site}", "osv": ["scan", "source", "--lockfile", str(work / "requirements.txt")],
            "secrets_dir": unpacked, "secrets_exclude": [], "licence": pypi_licence(meta["info"])}


def prepare_mcpb(artifact, entry, work, http, extra):
    data, _ = http.get(artifact["identifier"], limit=verify_mcp_identity.MAX_BYTES)
    if hashlib.sha256(data).hexdigest() != artifact["sha256"]:
        raise ValueError("MCP bundle does not match the pinned sha256")
    archive, bundle = work / "bundle.mcpb", work / "bundle"
    archive.write_bytes(data)
    bundle.mkdir()
    safe_extract_zip(archive, bundle)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    command = node_command(entry, bundle, mcpb_entry_point(manifest), extra)
    # A bundle ships its dependencies inside; osv-scanner reads them from the SBOM syft builds of the bundle.
    return {"command": command, "sbom": f"dir:{bundle}", "osv": None, "secrets_dir": bundle,
            "secrets_exclude": ["node_modules"], "licence": manifest.get("license")}


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


SCANNED = ("npm", "oci", "pypi", "mcpb")


def scan_package(artifact, entry, work, reports, http, record=None):
    package_record = next((p for p in ((record or {}).get("server") or {}).get("packages", [])
                           if p.get("registryType") == artifact["registry"] and p.get("identifier") == artifact["identifier"]), None)
    extra = server_args(entry, package_record)
    preparers = {"npm": lambda: prepare_npm(artifact, entry, work, http, extra),
                 "pypi": lambda: prepare_pypi(artifact, entry, work, http, extra),
                 "mcpb": lambda: prepare_mcpb(artifact, entry, work, http, extra),
                 "oci": lambda: prepare_oci(artifact, entry, work, extra)}
    if artifact["registry"] not in preparers:
        raise NotScannable(f"{artifact['registry']} packages are not supported by the L2 scanner yet")
    prepared = preparers[artifact["registry"]]()
    stem = f"{artifact['registry']}-{hashlib.sha256(artifact['identifier'].encode()).hexdigest()[:8]}"
    listing = mcp_tools_list.list_tools(prepared["command"], timeout=120)
    (reports / f"{stem}-tools.json").write_text(json.dumps(listing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sbom_path = reports / f"{stem}-sbom.cdx.json"
    run(["syft", "scan", prepared["sbom"], "--quiet", "-o", f"cyclonedx-json={sbom_path}"])
    osv_path = reports / f"{stem}-osv.json"
    osv_args = prepared["osv"] or ["scan", "source", "--lockfile", str(sbom_path)]
    osv = subprocess.run(["osv-scanner", *osv_args, "--format", "json", "--output", str(osv_path)],
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
    per_package, problems, blocking = [], [], False
    packages = [a for a in entry["artifacts"] if a["kind"] == "package"]
    # L2 needs every package scanned; with an unsupported one the entry keeps what its identity evidence supports.
    unsupported = sorted({a["registry"] for a in packages if a["registry"] not in SCANNED})
    if len(pins) == len(packages) and not unsupported:
        for artifact in packages:
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    per_package.append(scan_package(artifact, entry, pathlib.Path(tmp), reports, http, record))
                except (mcp_tools_list.McpError, NotScannable) as error:
                    # The server did not list its tools offline: no L2, but the identity evidence still stands.
                    problems.append(f"{artifact['identifier']}: {error}")
                except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
                    problems.append(f"{artifact['identifier']}: {error}")
                    blocking = True
    if packages and len(per_package) == len(packages):
        evidence, level = assemble(evidence, entry, per_package, versions)
    elif blocking or len(pins) != len(packages):
        level = "L0"
    else:
        level = mcp_evidence.validate_evidence(evidence, entry)
    path = out / f"{entry['version']}.json"
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{entry['id']} {entry['version']}: evidence supports {level}")
    if unsupported:
        print(f"  not scanned: {', '.join(unsupported)} packages are not supported by the L2 scanner yet")
    for check in mcp_evidence.IDENTITY_CHECKS:
        print(f"  identity.{check}: {evidence['identity'][check]['result']} - {evidence['identity'][check]['details']}")
    for scan, result in evidence.get("scans", {}).items():
        print(f"  {scan}: {result['result']} - {result['details'][:300]}")
    for problem in problems:
        print(f"  error: {problem}"[:600])
    # Exit 1 only when the evidence had to drop to L0; a server that cannot list its tools offline is reported above.
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
