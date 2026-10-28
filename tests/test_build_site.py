import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site


class BuildSiteTests(unittest.TestCase):
    def test_builds_every_skill_without_external_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp)
            count = build_site.build(out)
            page = (out / "index.html").read_text(encoding="utf-8")
            skills = [i["id"] for i in json.loads((ROOT / "registry/catalog.json").read_text())["items"] if i["type"] == "skill"]
            self.assertEqual(count, len(skills))
            for skill_id in skills:
                self.assertIn(f">{skill_id}</a>", page)
            self.assertNotIn("<script src", page)
            self.assertNotIn("stylesheet", page)
            self.assertTrue((out / "catalog.json").is_file())
            self.assertNotIn("{{", page)
            self.assertIn(f"<b>{len(skills)}</b><span>skills</span>", page)

    def test_descriptions_are_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_site.build(pathlib.Path(tmp))
            page = (pathlib.Path(tmp) / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("<document>", page)


if __name__ == "__main__":
    unittest.main()
