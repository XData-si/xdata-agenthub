"""Seals are bound to package digests and become stale when a skill changes."""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import seal  # noqa: E402


class SealTests(unittest.TestCase):
    def test_repository_seals_are_current(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/seal.py"), "check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_stale_and_missing_prerequisite_are_reported(self):
        digests = {"demo": "a" * 64}
        data = {"schema_version": 1, "seals": {"demo": [
            {"level": "verified", "digest": "b" * 64, "granted": "2026-10-28", "by": "m", "evidence": "README.md"}]}}
        problems = seal.check(data, digests)
        self.assertTrue(any("stale" in p for p in problems))
        self.assertTrue(any("requires the 'reviewed' seal" in p for p in problems))

    def test_unknown_level_and_missing_evidence(self):
        data = {"schema_version": 1, "seals": {"demo": [
            {"level": "gold", "digest": "a" * 64, "granted": "2026-10-28", "by": "m", "evidence": "docs/nope.md"}]}}
        problems = seal.check(data, {"demo": "a" * 64})
        self.assertTrue(any("unknown level" in p for p in problems))
        self.assertTrue(any("not found" in p for p in problems))

    def test_valid_seal_passes(self):
        data = {"schema_version": 1, "seals": {"demo": [
            {"level": "reviewed", "digest": "a" * 64, "granted": "2026-10-28", "by": "m", "evidence": "README.md"}]}}
        self.assertEqual(seal.check(data, {"demo": "a" * 64}), [])


if __name__ == "__main__":
    unittest.main()
