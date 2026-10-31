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
sys.path.insert(0, str(ROOT / "tests"))
import trusted_sources
from test_extra_catalogs_user_scope import skill_item, write_catalog, write_skill

PREFIX = "https://raw.githubusercontent.com/example/catalog/"


def write_policy(directory, **fields):
    data = {"schema_version": 1, "refresh_url_prefixes": [PREFIX], "catalog_dirs": ["trusted"]}
    data.update(fields)
    path = pathlib.Path(directory) / "trusted-sources.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class PolicyTests(unittest.TestCase):
    def test_no_policy_allows_everything(self):
        self.assertIsNone(trusted_sources.load_policy(""))
        trusted_sources.check_refresh_url(None, "https://anywhere.example/x.json")
        trusted_sources.check_catalog(None, "/tmp/catalog.json")

    def test_prefixes_and_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = trusted_sources.load_policy(write_policy(tmp))
            trusted_sources.check_refresh_url(policy, PREFIX + "0" * 40 + "/registry/catalog.json")
            for url in ("https://raw.githubusercontent.com/example/catalog-evil/x.json",
                        "https://raw.githubusercontent.com/other/catalog/x.json"):
                with self.assertRaises(ValueError):
                    trusted_sources.check_refresh_url(policy, url)
            inside = pathlib.Path(tmp) / "trusted" / "org" / "catalog.json"
            trusted_sources.check_catalog(policy, inside)  # relative catalog_dirs resolve next to the policy file
            for outside in (pathlib.Path(tmp) / "catalog.json", pathlib.Path(tmp) / "trusted-evil" / "catalog.json",
                            pathlib.Path(tmp) / "trusted" / ".." / "catalog.json"):
                with self.assertRaises(ValueError):
                    trusted_sources.check_catalog(policy, outside)

    def test_rejects_unsafe_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            for fields in ({"refresh_url_prefixes": ["http://example.com/"]},
                           {"refresh_url_prefixes": ["https://example.com/org"]},
                           {"refresh_url_prefixes": ["https://user:secret@example.com/"]},
                           {"refresh_url_prefixes": ["https://example.com/?a=b/"]},
                           {"catalog_dirs": [""]}, {"catalog_dirs": "trusted"},
                           {"schema_version": 2}, {"unknown": True}):
                with self.subTest(fields=fields), self.assertRaises(ValueError):
                    trusted_sources.load_policy(write_policy(tmp, **fields))
            real = write_policy(tmp)
            link = pathlib.Path(tmp) / "link.json"
            try:
                link.symlink_to(real)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                trusted_sources.load_policy(link)


class CliTests(unittest.TestCase):
    def run_cli(self, *args, env=None):
        merged = {k: v for k, v in os.environ.items() if k not in ("XAH_CATALOGS", trusted_sources.POLICY_ENV)}
        merged.update(env or {})
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=merged)

    def test_additional_catalog_must_be_in_a_trusted_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = write_policy(tmp)
            trusted_dir, other_dir = pathlib.Path(tmp) / "trusted", pathlib.Path(tmp) / "other"
            trusted = write_catalog(trusted_dir, [skill_item("org-trusted", write_skill(trusted_dir, "org-trusted"))])
            other = write_catalog(other_dir, [skill_item("org-other", write_skill(other_dir, "org-other"))])
            listed = self.run_cli("--trusted-sources", str(policy), "--catalog", str(trusted), "list")
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("org-trusted", listed.stdout)
            refused = self.run_cli("--catalog", str(other), "list", env={trusted_sources.POLICY_ENV: str(policy)})
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("outside the trusted catalog_dirs", refused.stdout + refused.stderr)

    def test_refresh_url_outside_policy_is_refused_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = write_policy(tmp)
            revision = "0" * 40
            result = self.run_cli("--trusted-sources", str(policy), "catalog-refresh",
                                  "--url", f"https://evil.example/{revision}/catalog.json", "--revision", revision,
                                  "--sha256", "a" * 64, "--approve", "--offline")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not allowed by the trusted sources policy", result.stdout + result.stderr)
            allowed = self.run_cli("--trusted-sources", str(policy), "catalog-refresh",
                                   "--url", f"{PREFIX}{revision}/catalog.json", "--revision", revision,
                                   "--sha256", "a" * 64, "--approve", "--offline")
            self.assertIn("Offline mode", allowed.stdout + allowed.stderr)  # passed the policy, stopped by --offline

    def test_doctor_reports_the_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("--trusted-sources", str(write_policy(tmp)), "doctor")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 refresh URL prefixes, 1 catalog directories", result.stdout)


if __name__ == "__main__":
    unittest.main()
