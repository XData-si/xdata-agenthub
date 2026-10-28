import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cli"))
from adapter_contract import CONTRACT_VERSION, USER_ADAPTERS, adapter_spec, destination_for

class AdapterContractTests(unittest.TestCase):
    def test_runtime_paths(self):
        self.assertEqual(str(destination_for("claude", "code-review", "skill")), ".claude/skills/code-review")
        self.assertEqual(str(destination_for("codex", "code-review", "skill")), ".agents/skills/code-review")
        self.assertEqual(str(destination_for("opencode", "code-review", "skill")), ".opencode/skills/code-review")
    def test_guidance_paths(self):
        self.assertEqual(str(destination_for("claude", "project-agents", "instruction")), "CLAUDE.md")
        self.assertEqual(str(destination_for("codex", "project-agents", "instruction")), "AGENTS.md")
    def test_invalid_identifier(self):
        for value in ("../escape", "Bad", "a--b", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                destination_for("claude", value, "skill")
    def test_unknown_agent(self):
        with self.assertRaises(ValueError):
            adapter_spec("unknown")
    def test_contract_version_and_user_scope_are_explicit(self):
        self.assertEqual(CONTRACT_VERSION, 2)
        self.assertEqual(set(USER_ADAPTERS), {"claude", "codex", "opencode"})
