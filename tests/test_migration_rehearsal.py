"""Offline integration rehearsal for migration and complete backup/restore."""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli/xah.py"


class MigrationRehearsal(unittest.TestCase):
    def cli(self, *args, expected=0):
        p = subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT,
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
        return p.stdout

    def test_backup_restore_and_modified_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            base = pathlib.Path(d)
            project = base / "project"
            backup = base / "backup"
            restored = base / "restored"
            project.mkdir()
            self.cli("add", "code-review", "--target", str(project))
            self.cli("status", "--target", str(project))
            shutil.copytree(project, backup)
            tracked = project / "skills/code-review/SKILL.md"
            tracked.write_text("operator local edit", encoding="utf-8")
            self.cli("update", "code-review", "--target", str(project), "--dry-run", expected=2)
            self.cli("update", "code-review", "--target", str(project), "--apply", expected=1)
            self.assertEqual(tracked.read_text(encoding="utf-8"), "operator local edit")
            shutil.copytree(backup, restored)
            self.assertEqual((restored / ".xah-installed.json").read_bytes(),
                             (backup / ".xah-installed.json").read_bytes())
            self.assertEqual((restored / "skills/code-review/SKILL.md").read_bytes(),
                             (backup / "skills/code-review/SKILL.md").read_bytes())
            self.assertIn("untouched", self.cli("status", "--target", str(restored)))

    def test_docs_exist_and_reference_commands(self):
        migration = (ROOT / "docs/MIGRATION_v0.2.0.md").read_text(encoding="utf-8")
        runbook = (ROOT / "docs/OPERATOR_RUNBOOK.md").read_text(encoding="utf-8")
        for phrase in ("--dry-run", "--apply", ".xah-installed.json", "v0.1.0"):
            self.assertIn(phrase, migration)
        for phrase in ("status", "audit", "ROLLBACK INCOMPLETE"):
            self.assertIn(phrase, runbook)


if __name__ == "__main__":
    unittest.main()
