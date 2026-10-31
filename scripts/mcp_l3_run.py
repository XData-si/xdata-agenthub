#!/usr/bin/env python3
"""Verified MCP level L3 (draft): run one catalog entry's test plan in a gVisor sandbox and record its activity.

Runs in CI only (needs Docker and the gVisor runtime `runsc-trace`, see .github/workflows/mcp-runtime.yml):
1. fetch the pinned package exactly as the L2 scan does (sha256 checked, npm --ignore-scripts);
2. create an internal Docker network whose only other member is the plan's fixture (no route to the internet);
3. start the server under gVisor with strace, read-only root, no capabilities, no credentials;
4. run the plan's positive and negative tool calls (registry/mcp-plans/<id>.json);
5. parse file, network and process activity from the gVisor strace log and compare it with the plan's profile.

Writes OUT/<id>/<version>-runtime.json and the raw gVisor logs. Nothing is committed and no level is changed.

  python3 scripts/mcp_l3_run.py playwright --out "$RUNNER_TEMP/mcp-runtime" --runsc-logs /tmp/runsc
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
sys.path.insert(0, str(ROOT / "scripts"))
import mcp_catalog
import mcp_l2_scan
import mcp_tools_list
import verify_mcp_identity
from import_mcp_registry import CATALOG

PLANS = ROOT / "registry" / "mcp-plans"
FIXTURE_IMAGE = mcp_l2_scan.PYTHON_IMAGE
RUNTIME = "runsc-trace"
SANDBOX = ["--rm", "-i", "--read-only", "--tmpfs", "/tmp:rw,size=512m", "--shm-size", "512m", "--cap-drop", "ALL",
           "--security-opt", "no-new-privileges", "--pids-limit", "512", "--memory", "2g", "--user", "65534:65534",
           "-e", "HOME=/tmp"]
WRITE_FLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND")
# Paths every process touches while starting; never reported as activity.
NOISE = ("/proc/", "/sys/", "/dev/null", "/dev/urandom", "/dev/random", "/dev/shm/", "/dev/pts", "/dev/tty")


def load_plan(entry):
    path = PLANS / f"{entry['id']}.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("schema_version") != 1 or plan.get("server") != entry["id"] or plan.get("version") != entry["version"]:
        raise ValueError(f"{path.name} does not describe {entry['id']} {entry['version']}")
    if plan.get("package") != "npm":
        raise ValueError("only npm packages have a runtime harness so far")
    return plan, hashlib.sha256(path.read_bytes()).hexdigest()


# --- gVisor strace parsing -------------------------------------------------------------------------------------------
# Lines look like: I1031 10:00:00.000001  1 strace.go:614] [  12:  12] node X openat(AT_FDCWD /app, 0x7f.. /app/cli.js,
# O_RDONLY|O_CLOEXEC, 0o0) = 21 (0x15) (8.1µs). Only exit (X) lines are used, so the result is known.
LINE = re.compile(r"\]\s+\[\s*\d+:\s*\d+\]\s+(?P<comm>\S+)\s+X\s+(?P<call>[a-z0-9_]+)\((?P<args>.*)\)\s+=\s+(?P<ret>\S+)")
PATH = re.compile(r"0x[0-9a-f]+ (/[^,\s)]*)")
INET = re.compile(r"Family: AF_INET6?, Addr: \[?([0-9a-fA-F.:]*)\]?, Port: (\d+)")


def parse_strace(lines):
    """File writes and reads, network connections and executed programs from gVisor strace exit lines."""
    activity = {"writes": set(), "reads": set(), "connects": set(), "execs": set(), "unix": set()}
    for line in lines:
        match = LINE.search(line)
        if not match or match["ret"].startswith("-") or "errno=" in line[match.end("ret"):]:
            continue  # failed calls changed nothing
        call, args = match["call"], match["args"]
        paths = PATH.findall(args)
        if call in ("openat", "open", "creat"):
            if paths and not paths[-1].startswith(NOISE):
                kind = "writes" if call == "creat" or any(f in args for f in WRITE_FLAGS) else "reads"
                activity[kind].add(paths[-1])
        elif call in ("unlinkat", "unlink", "renameat", "renameat2", "rename", "mkdirat", "mkdir"):
            activity["writes"].update(p for p in paths if not p.startswith(NOISE))
        elif call == "connect":
            inet = INET.search(args)
            if inet:
                activity["connects"].add(f"{inet[1]}:{inet[2]}")
            elif "AF_UNIX" in args:
                activity["unix"].add((PATH.findall(args) or ["(abstract)"])[-1])
        elif call in ("execve", "execveat") and paths:
            activity["execs"].add(paths[0])
    return {k: sorted(v) for k, v in activity.items()}


def compare(activity, allowed, fixture_ips):
    """Mismatches between observed activity and the plan's allowlist (empty list = profile holds)."""
    mismatches = []
    write_paths = tuple(p.rstrip("/") + "/" for p in allowed.get("write_paths", []))
    for path in activity["writes"]:
        if not (path + "/").startswith(write_paths):
            mismatches.append(f"write outside allowed paths: {path}")
    loopback = ("127.", "::1", "0.0.0.0")
    for target in activity["connects"]:
        address = target.rsplit(":", 1)[0]
        if not address.startswith(loopback) and address not in fixture_ips:
            mismatches.append(f"connection to a host outside the allowlist: {target}")
    executables = tuple(allowed.get("executables", []))
    for program in activity["execs"]:
        if not program.startswith(executables):
            mismatches.append(f"executed a program outside the allowlist: {program}")
    return mismatches


# --- running the plan ------------------------------------------------------------------------------------------------
def call_text(result):
    return "\n".join(c.get("text", "") for c in result.get("content", []) if isinstance(c, dict))


def run_calls(client, plan):
    outcomes = []
    for step in plan["calls"]:
        try:
            result = client.request("tools/call", {"name": step["tool"], "arguments": step["arguments"]})
            failed, text = bool(result.get("isError")), call_text(result)
        except mcp_tools_list.McpError as error:
            failed, text = True, str(error)
        passed = (failed if step["expect"] == "error" else not failed and step.get("expect_text", "") in text)
        outcomes.append({"name": step["name"], "tool": step["tool"], "expect": step["expect"],
                         "result": "pass" if passed else "fail", "excerpt": text[:300]})
    return outcomes


def docker(*argv, check=True):
    return mcp_l2_scan.run(["docker", *argv]) if check else subprocess.run(["docker", *argv], capture_output=True, text=True)


def run_plan(entry, plan, work, runsc_logs, http):
    artifact = next(a for a in entry["artifacts"] if a["kind"] == "package" and a["registry"] == "npm")
    evidence = verify_mcp_identity.verify(entry, http)
    pins = {(p["registry"], p["identifier"]): p["sha256"] for p in evidence["artifacts"]}
    artifact = dict(artifact, sha256=pins[(artifact["registry"], artifact["identifier"])])
    package = pathlib.Path(mcp_l2_scan.prepare_npm(artifact, entry, work, http, [])["secrets_dir"])
    binary = mcp_l2_scan.npm_bin(json.loads((package / "package.json").read_text(encoding="utf-8")))
    tag = uuid.uuid4().hex[:10]
    network, names = f"xah-l3-{tag}", []
    docker("network", "create", "--internal", network)
    try:
        fixture_ips = []
        for fixture in plan["fixtures"]:
            name = f"xah-l3-{fixture['host']}-{tag}"
            docker("run", "-d", "--rm", "--name", name, "--network", network, "--network-alias", fixture["host"],
                   "--read-only", "--cap-drop", "ALL", "--user", "65534:65534",
                   "-v", f"{ROOT / fixture['root']}:/srv:ro", FIXTURE_IMAGE,
                   "python", "-m", "http.server", str(fixture["port"]), "--directory", "/srv")
            names.append(name)
            fixture_ips.append(docker("inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", name).strip())
        cidfile = work / "server.cid"
        command = ["docker", "run", "--runtime", RUNTIME, "--cidfile", str(cidfile), "--network", network, *SANDBOX,
                   "-v", f"{package}:/app:ro", "-w", "/tmp", plan["image"], "node", f"/app/{binary}", *plan["args"]]
        client = mcp_tools_list.StdioClient(command, timeout=120)
        try:
            client.request("initialize", {"protocolVersion": mcp_tools_list.PROTOCOL_VERSION, "capabilities": {},
                                          "clientInfo": {"name": "xdata-agenthub-verifier", "version": "1"}})
            client.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            tools = client.request("tools/list").get("tools", [])
            outcomes = run_calls(client, plan)
        finally:
            client.close()
            stderr = client.stderr[-20:]
        container = cidfile.read_text().strip() if cidfile.exists() else ""
    finally:
        for name in names:
            docker("rm", "-f", name, check=False)
        docker("network", "rm", network, check=False)
    # The runtime is configured with --debug-log=<dir>/%ID%/, so each container's logs are in a directory of its own.
    logs = sorted(p for p in (pathlib.Path(runsc_logs) / container).glob("*") if p.is_file()) if container else []
    lines = [line for log in logs for line in log.read_text(encoding="utf-8", errors="replace").splitlines()]
    activity = parse_strace(lines)
    return {"artifacts": evidence["artifacts"], "tools": len(tools), "calls": outcomes, "activity": activity,
            "mismatches": compare(activity, plan["allowed"], fixture_ips), "fixture_ips": fixture_ips,
            "strace_lines": len(lines), "logs": [str(p) for p in logs], "server_stderr": stderr}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("id")
    parser.add_argument("--out", required=True)
    parser.add_argument("--runsc-logs", required=True)
    args = parser.parse_args(argv)
    servers = mcp_catalog.validate_mcp_catalog(json.loads(CATALOG.read_text(encoding="utf-8")))
    entry = next((s for s in servers if s["id"] == args.id), None)
    if entry is None:
        parser.error(f"unknown id {args.id}")
    plan, plan_digest = load_plan(entry)
    out = pathlib.Path(args.out) / entry["id"]
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        report = run_plan(entry, plan, pathlib.Path(tmp), args.runsc_logs, verify_mcp_identity.Http())
    calls_ok = all(c["result"] == "pass" for c in report["calls"])
    report = {"id": entry["id"], "version": entry["version"], "plan_sha256": plan_digest, "profile": plan["profile"],
              "result": "pass" if calls_ok and not report["mismatches"] and report["strace_lines"] else "fail", **report}
    (out / f"{entry['version']}-runtime.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                          encoding="utf-8")
    for log in report["logs"]:
        shutil.copy(log, out / pathlib.Path(log).name)
    print(f"{entry['id']} {entry['version']}: runtime {report['result']} ({report['strace_lines']} strace lines)")
    for call in report["calls"]:
        print(f"  call {call['result']}: {call['name']} ({call['tool']}, expect {call['expect']})")
    for kind in ("writes", "connects", "execs", "unix"):
        print(f"  {kind}: {', '.join(report['activity'][kind][:20]) or 'none'}")
    for mismatch in report["mismatches"]:
        print(f"  mismatch: {mismatch}")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
