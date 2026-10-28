import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "xah.py"
sys.path.insert(0, str(ROOT / "cli"))
from adapter_contract import adapter_spec, destination_for


def write_catalog(directory, items):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "catalog.json"
    path.write_text(json.dumps({"schema_version": 1, "items": items}), encoding="utf-8")
    return path


def skill_item(item_id, path):
    return {"id": item_id, "type": "skill", "name": item_id, "description": "Private test skill",
            "path": path, "license": "Proprietary", "source": "Test organisation", "targets": ["claude"]}


def write_skill(directory, item_id, extra_file=None):
    skill = directory / "skills" / item_id
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {item_id}\ndescription: Private test skill\n---\n", encoding="utf-8")
    if extra_file:
        (skill / "references").mkdir()
        (skill / "references" / extra_file).write_text("local defaults\n", encoding="utf-8")
    return f"skills/{item_id}/SKILL.md"


class ExtraCatalogTests(unittest.TestCase):
    def run_cli(self, *args, env=None):
        merged = dict(os.environ)
        merged.pop("XAH_CATALOGS", None)
        merged.update(env or {})
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=merged)

    def test_list_includes_additional_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            org = pathlib.Path(tmp) / "org"
            catalog = write_catalog(org, [skill_item("org-deploy", write_skill(org, "org-deploy"))])
            result = self.run_cli("--catalog", str(catalog), "list")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("org-deploy", result.stdout)
            self.assertIn("code-review", result.stdout)

    def test_environment_variable_and_doctor(self):
        with tempfile.TemporaryDirectory() as tmp:
            org = pathlib.Path(tmp) / "org"
            catalog = write_catalog(org, [skill_item("org-deploy", write_skill(org, "org-deploy"))])
            result = self.run_cli("doctor", env={"XAH_CATALOGS": str(catalog)})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(catalog.resolve()), result.stdout)
            self.assertIn("all local paths valid", result.stdout)

    def test_add_from_additional_catalog_copies_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            org = pathlib.Path(tmp) / "org"
            target = pathlib.Path(tmp) / "project"
            target.mkdir()
            catalog = write_catalog(org, [skill_item("org-deploy", write_skill(org, "org-deploy", "defaults.md"))])
            result = self.run_cli("--catalog", str(catalog), "add", "org-deploy", "--agent", "claude", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".claude/skills/org-deploy/SKILL.md").is_file())
            self.assertTrue((target / ".claude/skills/org-deploy/references/defaults.md").is_file())

    def test_duplicate_id_across_catalogs_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            org = pathlib.Path(tmp) / "org"
            catalog = write_catalog(org, [skill_item("code-review", write_skill(org, "code-review"))])
            result = self.run_cli("--catalog", str(catalog), "list")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Duplicate item ID across catalogs: code-review", result.stderr)

    def test_missing_additional_catalog_is_refused(self):
        result = self.run_cli("--catalog", "/nonexistent/xah/catalog.json", "list")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Additional catalog not found", result.stderr)

    def test_path_outside_additional_catalog_root_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            outside = write_skill(base, "org-escape")
            org = base / "org"
            org.mkdir()
            (org / "skills").symlink_to(base / "skills")
            catalog = write_catalog(org, [skill_item("org-escape", outside)])
            target = base / "project"
            target.mkdir()
            result = self.run_cli("--catalog", str(catalog), "add", "org-escape", "--target", str(target))
            self.assertEqual(result.returncode, 1)
            self.assertFalse((target / "skills/org-escape").exists())


class UserScopeTests(unittest.TestCase):
    def run_cli(self, home, *args):
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
        env.pop("XAH_CATALOGS", None)
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=env)

    def test_user_paths(self):
        self.assertEqual(str(destination_for("claude", "code-review", "skill", "user")), ".claude/skills/code-review")
        self.assertEqual(str(destination_for("codex", "code-review", "skill", "user")), ".agents/skills/code-review")
        self.assertEqual(str(destination_for("opencode", "code-review", "skill", "user")), ".config/opencode/skills/code-review")

    def test_project_paths_unchanged(self):
        self.assertEqual(str(destination_for("opencode", "code-review", "skill")), ".opencode/skills/code-review")
        self.assertEqual(str(destination_for("claude", "project-agents", "instruction")), "CLAUDE.md")

    def test_user_scope_rejects_generic_and_instructions(self):
        with self.assertRaises(ValueError):
            adapter_spec("generic", "user")
        with self.assertRaises(ValueError):
            destination_for("claude", "project-agents", "instruction", "user")
        with self.assertRaises(ValueError):
            adapter_spec("claude", "system")

    def test_add_user_scope_installs_under_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = pathlib.Path(tmp)
            result = self.run_cli(home, "add", "code-review", "--agent", "opencode", "--scope", "user")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / ".config/opencode/skills/code-review/SKILL.md").is_file())
            self.assertFalse((home / ".opencode").exists())
            again = self.run_cli(home, "add", "code-review", "--agent", "opencode", "--scope", "user")
            self.assertNotEqual(again.returncode, 0)

    def test_update_user_scope_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = pathlib.Path(tmp)
            self.assertEqual(self.run_cli(home, "add", "code-review", "--agent", "claude", "--scope", "user").returncode, 0)
            result = self.run_cli(home, "update", "code-review", "--agent", "claude", "--scope", "user", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("skip       .claude/skills/code-review/SKILL.md", result.stdout)

    def test_user_scope_refuses_instruction_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = pathlib.Path(tmp)
            result = self.run_cli(home, "add", "project-agents", "--agent", "claude", "--scope", "user")
            self.assertEqual(result.returncode, 1)
            self.assertIn("supports skill items only", result.stderr)
            self.assertFalse((home / ".claude").exists())

    def test_user_scope_generic_agent_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(pathlib.Path(tmp), "add", "code-review", "--scope", "user")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Unsupported agent adapter for user scope", result.stderr)


if __name__ == "__main__":
    unittest.main()
