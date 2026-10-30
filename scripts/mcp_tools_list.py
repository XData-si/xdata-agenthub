#!/usr/bin/env python3
"""Read the tools/list result of a stdio MCP server (standard library only).

Starts the given command, performs the MCP handshake (initialize, notifications/initialized), pages through
tools/list and stops the server. No tool is called. The caller is responsible for isolation: the Verified MCP workflow
runs the command inside a container without network and without credentials (docs/VERIFIED_MCP.md).

  python3 scripts/mcp_tools_list.py --out tools.json -- docker run --rm -i --network none IMAGE@sha256:...
"""
import argparse
import json
import queue
import subprocess
import sys
import threading
import time

PROTOCOL_VERSION = "2025-06-18"
MAX_LINE = 4 * 1024 * 1024
MAX_PAGES = 50


class McpError(Exception):
    pass


class StdioClient:
    def __init__(self, argv, timeout=60, env=None):
        self.timeout = timeout
        self.process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env=env)
        self.lines = queue.Queue()
        self.stderr = []
        threading.Thread(target=self._read, args=(self.process.stdout, self.lines), daemon=True).start()
        threading.Thread(target=self._drain, daemon=True).start()
        self.next_id = 0

    @staticmethod
    def _read(stream, lines):
        for line in iter(lambda: stream.readline(MAX_LINE), b""):
            lines.put(line)
        lines.put(None)

    def _drain(self):
        for line in iter(self.process.stderr.readline, b""):
            if len(self.stderr) < 200:
                self.stderr.append(line.decode("utf-8", "replace").rstrip())

    def send(self, message):
        self.process.stdin.write(json.dumps(message).encode() + b"\n")
        self.process.stdin.flush()

    def request(self, method, params=None):
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": self.next_id, "method": method, **({"params": params} if params else {})})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise McpError(f"no response to {method} within {self.timeout}s")
            try:
                line = self.lines.get(timeout=remaining)
            except queue.Empty:
                continue
            if line is None:
                raise McpError(f"server exited before answering {method}: " + " | ".join(self.stderr[-5:]))
            try:
                message = json.loads(line)
            except ValueError:
                continue  # servers sometimes log to stdout; ignore lines that are not JSON-RPC
            if not isinstance(message, dict) or message.get("id") != self.next_id:
                if isinstance(message, dict) and "method" in message and "id" in message:
                    # Server-to-client request (sampling, roots, elicitation): refuse, we only list tools.
                    self.send({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": "not supported"}})
                continue
            if "error" in message:
                raise McpError(f"{method} failed: {json.dumps(message['error'])[:300]}")
            return message.get("result", {})

    def close(self):
        try:
            self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()


def list_tools(argv, timeout=60, env=None):
    client = StdioClient(argv, timeout, env)
    try:
        init = client.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                             "clientInfo": {"name": "xdata-agenthub-verifier", "version": "1"}})
        client.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, cursor = [], None
        for _ in range(MAX_PAGES):
            page = client.request("tools/list", {"cursor": cursor} if cursor else None)
            if not isinstance(page.get("tools"), list):
                raise McpError("tools/list result has no tools array")
            tools += page["tools"]
            cursor = page.get("nextCursor")
            if not cursor:
                break
        else:
            raise McpError(f"tools/list did not finish within {MAX_PAGES} pages")
        return {"protocolVersion": init.get("protocolVersion"), "serverInfo": init.get("serverInfo"), "tools": tools}
    finally:
        client.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a server command is required after --")
    try:
        result = list_tools(command, args.timeout)
    except McpError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"{len(result['tools'])} tools from {(result.get('serverInfo') or {}).get('name', 'server')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
