import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from recovery_journal import validate_journal

H = "a" * 64
T = "b" * 32


def valid():
    return {"schema_version": 1, "transaction_id": T, "item_id": "code-review",
            "state": "prepared", "operations": [{
                "action": "update", "path": "skills/code-review/SKILL.md",
                "original_sha256": H, "intended_sha256": "c" * 64,
                "backup_sha256": H, "completed": False}]}


class JournalValidationTests(unittest.TestCase):
    def test_valid_prepared_journal(self):
        data = valid()
        self.assertIs(validate_journal(data), data)

    def test_path_traversal_and_absolute_paths_refused(self):
        for path in ("../secret", "skills/../secret", "/etc/passwd", "C:/temp/a",
                     "skills//file", "skills/./file", "skills\\file", ""):
            with self.subTest(path=path):
                data = valid()
                data["operations"][0]["path"] = path
                with self.assertRaises(ValueError):
                    validate_journal(data)

    def test_duplicate_paths_refused(self):
        data = valid()
        data["operations"].append(copy.deepcopy(data["operations"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_journal(data)

    def test_bad_digest_refused(self):
        data = valid()
        data["operations"][0]["backup_sha256"] = "not-a-digest"
        with self.assertRaises(ValueError):
            validate_journal(data)

    def test_mismatched_backup_refused(self):
        data = valid()
        data["operations"][0]["backup_sha256"] = "d" * 64
        with self.assertRaises(ValueError):
            validate_journal(data)

    def test_invalid_transition_shape_refused(self):
        data = valid()
        data["state"] = "committed"
        with self.assertRaises(ValueError):
            validate_journal(data)
        data["state"] = "prepared"
        data["operations"][0]["completed"] = True
        with self.assertRaises(ValueError):
            validate_journal(data)

    def test_add_must_not_claim_backup(self):
        data = valid()
        op = data["operations"][0]
        op["action"] = "add"
        with self.assertRaises(ValueError):
            validate_journal(data)

    def test_unknown_fields_and_wrong_types_refused(self):
        data = valid()
        data["unexpected"] = 1
        with self.assertRaises(ValueError):
            validate_journal(data)
        data = valid()
        data["schema_version"] = True
        with self.assertRaises(ValueError):
            validate_journal(data)


if __name__ == "__main__":
    unittest.main()
