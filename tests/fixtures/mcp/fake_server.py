"""Minimal stdio MCP server for tests: two pages of tools, a log line on stdout, a server-to-client request."""
import json
import sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "ok"
TOOLS = [{"name": f"tool_{i}", "description": f"Tool {i}", "inputSchema": {"type": "object"}} for i in range(3)]

print("starting fake server (not JSON-RPC)", flush=True)
for line in sys.stdin:
    message = json.loads(line)
    if MODE == "exit":
        sys.exit(3)
    if "id" not in message or "method" not in message:
        continue
    if message["method"] == "initialize":
        result = {"protocolVersion": message["params"]["protocolVersion"], "capabilities": {"tools": {}},
                  "serverInfo": {"name": "fake", "version": "1.0"}}
        print(json.dumps({"jsonrpc": "2.0", "id": "srv-1", "method": "roots/list"}), flush=True)
    elif message["method"] == "tools/list":
        if MODE == "error":
            print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -1, "message": "boom"}}), flush=True)
            continue
        cursor = (message.get("params") or {}).get("cursor")
        result = {"tools": TOOLS[2:]} if cursor == "page-2" else {"tools": TOOLS[:2], "nextCursor": "page-2"}
    else:
        continue
    print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)
