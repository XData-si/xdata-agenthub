import io
import json
import pathlib
import sys
import tarfile
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import mcp_l2_scan as scanner
import test_mcp_evidence as base

entry, evidence, fixture = base.entry, base.evidence, base.fixture

PASS = {"result": "pass", "details": "ok"}
VERSIONS = {"syft": "syft 1.55.0", "osv": "osv-scanner 2.7.0", "gitleaks": "gitleaks 8.30.1"}


def package(tools=None, **overrides):
    data = {"tools": fixture("clean") if tools is None else tools, "sbom": PASS, "dependencies": PASS,
            "secrets": PASS, "licence": PASS}
    data.update(overrides)
    return data


def identity_only():
    doc = evidence()
    del doc["scans"], doc["tools"]
    return doc


class ResultTests(unittest.TestCase):
    def test_licence(self):
        self.assertEqual(scanner.licence_result("MIT", "MIT")["result"], "pass")
        self.assertEqual(scanner.licence_result("Apache-2.0", None)["result"], "pass")
        self.assertEqual(scanner.licence_result("MIT", "Apache-2.0")["result"], "fail")
        self.assertEqual(scanner.licence_result("BUSL-1.1", None)["result"], "fail")
        self.assertEqual(scanner.licence_result(None, "MIT")["result"], "fail")

    def test_osv_fails_on_high_or_unscored(self):
        report = lambda severity: {"results": [{"packages": [{"package": {"name": "lib", "version": "1.0"},
                                                               "groups": [{"ids": ["GHSA-x"], "max_severity": severity}]}]}]}
        self.assertEqual(scanner.osv_result(report("5.3"))["result"], "pass")
        self.assertEqual(scanner.osv_result(report("9.8"))["result"], "fail")
        unscored = scanner.osv_result(report(""))
        self.assertEqual(unscored["result"], "pass")
        self.assertIn("1 unscored", unscored["details"])
        self.assertEqual(scanner.osv_result({})["result"], "pass")

    def test_secrets_and_sbom(self):
        self.assertEqual(scanner.gitleaks_result([])["result"], "pass")
        found = scanner.gitleaks_result([{"File": "/tmp/x/dist/a.js", "StartLine": 3, "RuleID": "aws-access-token"}], "/tmp/x")
        self.assertEqual(found["result"], "fail")
        self.assertIn("dist/a.js:3", found["details"])
        self.assertEqual(scanner.sbom_result({"components": [{}]})["result"], "pass")
        self.assertEqual(scanner.sbom_result({})["result"], "fail")

    def test_npm_bin_and_placeholders(self):
        self.assertEqual(scanner.npm_bin({"name": "@x/files", "bin": "cli.js"}), "cli.js")
        self.assertEqual(scanner.npm_bin({"name": "@x/files", "bin": {"other": "o.js", "files": "f.js"}}), "f.js")
        with self.assertRaises(ValueError):
            scanner.npm_bin({"name": "x"})
        env = scanner.placeholder_env(entry(environment=[
            {"name": "FILES_URL", "required": True, "secret": False},
            {"name": "FILES_TOKEN", "required": True, "secret": True},
            {"name": "FILES_ROOT", "required": False, "secret": False}]))
        self.assertEqual(env, {"FILES_URL": "http://127.0.0.1:9", "FILES_TOKEN": "xah-verifier-placeholder"})

    def test_server_args(self):
        record = {"packageArguments": [{"type": "positional", "value": "stdio"},
                                       {"type": "named", "name": "--read-only", "format": "boolean"},
                                       {"type": "named", "name": "--telemetry", "default": "enabled"},
                                       {"type": "named", "name": "--toolsets", "value": "repos"},
                                       {"type": "named", "name": "--mode", "default": "local", "isRequired": True},
                                       {"type": "named", "name": "--token", "value": "{token}"}]}
        self.assertEqual(scanner.server_args(entry(), record), ["stdio", "--toolsets", "repos", "--mode", "local"])
        self.assertEqual(scanner.server_args(entry(id="grafana"), None), ["-t", "stdio"])

    def test_unsafe_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = pathlib.Path(tmp) / "p.tgz"
            with tarfile.open(archive, "w:gz") as tar:
                info = tarfile.TarInfo("../escape.txt")
                info.size = 1
                tar.addfile(info, io.BytesIO(b"x"))
            target = pathlib.Path(tmp) / "out"
            target.mkdir()
            with self.assertRaises(ValueError):
                scanner.safe_extract(archive, target)


    def test_unsafe_zip_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = pathlib.Path(tmp) / "b.mcpb"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("../escape.txt", "x")
            target = pathlib.Path(tmp) / "out"
            target.mkdir()
            with self.assertRaises(ValueError):
                scanner.safe_extract_zip(archive, target)

    def test_wheel_console_script_and_launcher(self):
        points = "[console_scripts]\nother = other.cli:run\nmcp-files = mcp_files.main:main [cli]\n\n[other]\nx = y:z\n"
        self.assertEqual(scanner.wheel_console_script(points, ["mcp_files", "mcp-files"]), "mcp_files.main:main")
        self.assertEqual(scanner.wheel_console_script(points, ["missing"]), "mcp_files.main:main")  # first by name
        with self.assertRaises(ValueError):
            scanner.wheel_console_script("[gui_scripts]\na = b:c\n", ["a"])
        code = scanner.python_launcher("mcp_files.main:app.run")
        self.assertIn("importlib.import_module('mcp_files.main').app.run()", code)
        with self.assertRaises(ValueError):
            scanner.python_launcher("os:system('id')")

    def test_pypi_licence_and_requirements(self):
        self.assertEqual(scanner.pypi_licence({"license_expression": "Apache-2.0"}), "Apache-2.0")
        self.assertEqual(scanner.pypi_licence({"license": None, "classifiers": [
            "License :: OSI Approved :: MIT License", "Programming Language :: Python"]}), "MIT")
        self.assertEqual(scanner.pypi_licence({"license": "Proprietary", "classifiers": []}), "Proprietary")
        with tempfile.TemporaryDirectory() as tmp:
            for name, version in (("httpx", "0.28.1"), ("mcp", "1.30.0")):
                info = pathlib.Path(tmp) / f"{name}-{version}.dist-info"
                info.mkdir()
                (info / "METADATA").write_text(f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n\nName: body\n")
            self.assertEqual(scanner.installed_requirements(tmp), "httpx==0.28.1\nmcp==1.30.0\n")

    def test_mcpb_entry_point(self):
        manifest = {"server": {"type": "node", "entry_point": "server/dist/index.mjs"}}
        self.assertEqual(scanner.mcpb_entry_point(manifest), "server/dist/index.mjs")
        with self.assertRaises(scanner.NotScannable):
            scanner.mcpb_entry_point({"server": {"type": "python", "entry_point": "main.py"}})
        for unsafe in ("/etc/passwd", "../x.js", ""):
            with self.assertRaises(ValueError):
                scanner.mcpb_entry_point({"server": {"type": "node", "entry_point": unsafe}})


class AssembleTests(unittest.TestCase):
    def test_clean_scan_supports_l2(self):
        doc, level = scanner.assemble(identity_only(), entry(), [package()], VERSIONS)
        self.assertEqual(level, "L2")
        self.assertEqual(doc["scans"]["dependencies"]["tool"], "osv-scanner 2.7.0")

    def test_any_failure_stops_at_l1(self):
        cases = [package(tools=fixture("poisoned")), package(tools=[]), package(secrets={"result": "fail", "details": "x"})]
        for case in cases:
            with self.subTest(case=json.dumps(case)[:60]):
                self.assertEqual(scanner.assemble(identity_only(), entry(), [case], VERSIONS)[1], "L1")

    def test_all_packages_must_pass_and_agree(self):
        failing = package(dependencies={"result": "fail", "details": "GHSA"})
        self.assertEqual(scanner.assemble(identity_only(), entry(), [package(), failing], VERSIONS)[1], "L1")
        other = package(tools=fixture("clean")[:1])
        doc, level = scanner.assemble(identity_only(), entry(), [package(), other], VERSIONS)
        self.assertEqual(level, "L1")
        self.assertIn("different tools", doc["scans"]["tools"]["details"])


if __name__ == "__main__":
    unittest.main()
