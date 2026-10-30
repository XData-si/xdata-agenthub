import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import mcp_tools_list

SERVER = [sys.executable, str(ROOT / "tests" / "fixtures" / "mcp" / "fake_server.py")]


class ToolsListTests(unittest.TestCase):
    def test_lists_all_pages_and_ignores_noise(self):
        result = mcp_tools_list.list_tools(SERVER, timeout=20)
        self.assertEqual([t["name"] for t in result["tools"]], ["tool_0", "tool_1", "tool_2"])
        self.assertEqual(result["serverInfo"]["name"], "fake")

    def test_server_errors_and_exits_are_reported(self):
        for mode in ("error", "exit"):
            with self.subTest(mode), self.assertRaises(mcp_tools_list.McpError):
                mcp_tools_list.list_tools(SERVER + [mode], timeout=20)

    def test_cli_writes_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "tools.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mcp_tools_list.main(["--out", str(out), "--", *SERVER]), 0)
            self.assertEqual(len(json.loads(out.read_text(encoding="utf-8"))["tools"]), 3)


if __name__ == "__main__":
    unittest.main()
