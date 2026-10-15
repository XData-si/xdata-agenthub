import json
import os
import pathlib
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

if __name__ == "__main__":
    unittest.main()
