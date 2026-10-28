"""Distribution metadata: Claude Code plugin marketplace and Agent Skills specification compliance."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "registry/catalog.json").read_text(encoding="utf-8"))
SKILL_IDS = {item["id"] for item in CATALOG["items"] if item["type"] == "skill"}
MARKETPLACE = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def frontmatter(skill_id):
    text = (ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
    header = text.split("---", 2)[1]
    fields = dict(re.findall(r"(?m)^([a-z-]+):\s*(.*)$", header))
    return text, fields


class AgentSkillsSpecTests(unittest.TestCase):
    """Constraints from https://agentskills.io/specification."""

    def test_name_rules(self):
        for skill_id in SKILL_IDS:
            with self.subTest(skill=skill_id):
                _, fields = frontmatter(skill_id)
                self.assertEqual(fields["name"], skill_id)
                self.assertLessEqual(len(skill_id), 64)
                self.assertRegex(skill_id, NAME)

    def test_description_length_and_trigger(self):
        for skill_id in SKILL_IDS:
            with self.subTest(skill=skill_id):
                _, fields = frontmatter(skill_id)
                description = fields["description"]
                self.assertTrue(20 <= len(description) <= 1024, len(description))
                self.assertRegex(description, r"\bUse (when|at|after|before|during)\b",
                                 "description must say when to use the skill")

    def test_body_size_and_reference_depth(self):
        for skill_id in SKILL_IDS:
            with self.subTest(skill=skill_id):
                text, _ = frontmatter(skill_id)
                self.assertLessEqual(len(text.splitlines()), 500)
                for link in re.findall(r"\]\(((?:references|assets|scripts)/[^)]+)\)", text):
                    self.assertTrue((ROOT / "skills" / skill_id / link).is_file(), link)
                    self.assertEqual(len(pathlib.PurePosixPath(link).parts), 2, "keep references one level deep")


class MarketplaceTests(unittest.TestCase):
    def plugins(self):
        return {plugin["name"]: plugin for plugin in MARKETPLACE["plugins"]}

    def test_required_fields(self):
        self.assertRegex(MARKETPLACE["name"], NAME)
        self.assertTrue(MARKETPLACE["owner"]["name"])
        for plugin in MARKETPLACE["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertRegex(plugin["name"], NAME)
                self.assertEqual(plugin["source"], "./")
                self.assertTrue(plugin["description"])
                self.assertEqual(plugin["license"], "MIT")

    def test_skill_paths_exist_and_stay_inside_repository(self):
        for plugin in MARKETPLACE["plugins"]:
            for path in plugin["skills"]:
                with self.subTest(plugin=plugin["name"], path=path):
                    self.assertTrue(path.startswith("./") and ".." not in path)
                    self.assertTrue((ROOT / path).is_dir())

    def test_all_bundle_covers_catalog(self):
        self.assertEqual(self.plugins()["xdata-agenthub"]["skills"], ["./skills/"])

    def test_every_skill_in_exactly_one_topic_bundle(self):
        listed = [path.removeprefix("./skills/") for name, plugin in self.plugins().items()
                  if name != "xdata-agenthub" for path in plugin["skills"]]
        self.assertEqual(len(listed), len(set(listed)), "skill listed in two topic bundles")
        self.assertEqual(set(listed), SKILL_IDS - {"agenthub-router"})

    def test_router_mentions_only_existing_skills(self):
        text, _ = frontmatter("agenthub-router")
        catalog_ids = {item["id"] for item in CATALOG["items"]}
        unknown = {ref for ref in re.findall(r"`([a-z0-9-]+)`", text) if ref not in catalog_ids}
        self.assertFalse(unknown, unknown)


if __name__ == "__main__":
    unittest.main()
