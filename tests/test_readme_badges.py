"""README trust badges must match the catalog and the seals, so the README never overstates what is reviewed."""
import collections
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReadmeBadgeTests(unittest.TestCase):
    def test_badge_counts_match_registry(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        catalog = json.loads((ROOT / "registry/catalog.json").read_text(encoding="utf-8"))["items"]
        seals = json.loads((ROOT / "registry/seals.json").read_text(encoding="utf-8"))["seals"]
        skills = sum(1 for item in catalog if item["type"] == "skill")
        levels = collections.Counter(seal["level"] for entries in seals.values() for seal in entries)
        expected = {
            r"badge/skills-(\d+)-": skills,
            r"badge/security%20reviewed-(\d+)%2F\d+-": levels["reviewed"],
            r"badge/security%20reviewed-\d+%2F(\d+)-": skills,
            r"badge/EU%20ready-(\d+)-": levels["eu-ready"],
            r"badge/runtime%20verified-(\d+)-": levels["verified"],
        }
        for pattern, count in expected.items():
            match = re.search(pattern, readme)
            self.assertIsNotNone(match, pattern)
            self.assertEqual(int(match.group(1)), count, pattern)


if __name__ == "__main__":
    unittest.main()
