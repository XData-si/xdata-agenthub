import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import mcp_l3_run as l3

PREFIX = "I1031 10:00:00.000001       1 strace.go:614] [  12:  12] node X "
LINES = [
    PREFIX + "openat(AT_FDCWD /, 0x7f00 /app/cli.js, O_RDONLY|O_CLOEXEC, 0o0) = 21 (0x15) (8.1µs)",
    PREFIX + "openat(AT_FDCWD /, 0x7f00 /tmp/playwright-output/page.yml, O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC, 0o644) = 22 (0x16) (9µs)",
    PREFIX + "openat(AT_FDCWD /, 0x7f00 /etc/passwd, O_RDWR, 0o0) = 23 (0x17) (5µs)",
    PREFIX + "openat(AT_FDCWD /, 0x7f00 /root/.ssh/id_rsa, O_RDONLY, 0o0) = 0 (0x0) errno=13 (permission denied) (3µs)",
    PREFIX + "openat(AT_FDCWD /, 0x7f00 /proc/self/maps, O_RDONLY, 0o0) = 24 (0x18) (2µs)",
    PREFIX + "connect(0x19 socket:[7], 0x7f10 {Family: AF_INET, Addr: 172.18.0.2, Port: 8000}, 0x10) = 0 (0x0) (40µs)",
    PREFIX + "connect(0x1a socket:[8], 0x7f10 {Family: AF_INET, Addr: 93.184.215.14, Port: 443}, 0x10) = 0 (0x0) (40µs)",
    PREFIX + "connect(0x1b socket:[9], 0x7f10 {Family: AF_INET, Addr: 8.8.8.8, Port: 53}, 0x10) = -1 errno=101 (network is unreachable) (1µs)",
    PREFIX + "connect(0x1c socket:[10], 0x7f10 {Family: AF_UNIX, Addr: 0x7f20 /tmp/.X11-unix/X0}, 0x10) = 0 (0x0) (3µs)",
    PREFIX + "execve(0x7f30 /ms-playwright/chromium-1200/chrome-linux/chrome, 0x7f40 [...], 0x7f50 [...]) = 0 (0x0) (1ms)",
    PREFIX + "execve(0x7f30 /bin/sh, 0x7f40 [...], 0x7f50 [...]) = 0 (0x0) (1ms)",
    "I1031 10:00:00.000002       1 strace.go:570] [  12:  12] node E openat(AT_FDCWD /, 0x7f00 /entry/only, O_WRONLY, 0o0)",
]


class StraceTests(unittest.TestCase):
    def test_parse_keeps_successful_calls_and_classifies_them(self):
        activity = l3.parse_strace(LINES)
        self.assertEqual(activity["reads"], ["/app/cli.js"])
        self.assertEqual(activity["writes"], ["/etc/passwd", "/tmp/playwright-output/page.yml"])
        self.assertEqual(activity["connects"], ["172.18.0.2:8000", "93.184.215.14:443"])
        self.assertEqual(activity["unix"], ["/tmp/.X11-unix/X0"])
        self.assertEqual(activity["execs"], ["/bin/sh", "/ms-playwright/chromium-1200/chrome-linux/chrome"])

    def test_compare_reports_each_mismatch(self):
        allowed = {"write_paths": ["/tmp"], "executables": ["/usr/bin/node", "/ms-playwright/"]}
        mismatches = l3.compare(l3.parse_strace(LINES), allowed, ["172.18.0.2"])
        self.assertEqual(mismatches, ["write outside allowed paths: /etc/passwd",
                                      "connection to a host outside the allowlist: 93.184.215.14:443",
                                      "executed a program outside the allowlist: /bin/sh"])
        clean = {"writes": ["/tmp/x"], "reads": [], "connects": ["127.0.0.1:9222", "172.18.0.2:8000"],
                 "execs": ["/usr/bin/node"], "unix": []}
        self.assertEqual(l3.compare(clean, allowed, ["172.18.0.2"]), [])
        self.assertEqual(l3.compare({**clean, "writes": ["/tmpfoo/x"]}, allowed, []),
                         ["write outside allowed paths: /tmpfoo/x", "connection to a host outside the allowlist: 172.18.0.2:8000"])

    def test_committed_plans_match_the_catalog(self):
        import json
        servers = {s["id"]: s for s in json.loads((ROOT / "registry/mcp-servers.json").read_text(encoding="utf-8"))["servers"]}
        for path in sorted((ROOT / "registry/mcp-plans").glob("*.json")):
            plan, digest = l3.load_plan(servers[path.stem])
            self.assertEqual(len(digest), 64)
            self.assertTrue(any(c["expect"] == "error" for c in plan["calls"]), "plans need negative cases")
            self.assertTrue(plan["image"].split("@")[-1].startswith("sha256:"), "fixture-free images are pinned")


if __name__ == "__main__":
    unittest.main()
