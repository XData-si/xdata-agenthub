#!/bin/bash
# Before/after demo harness: runs each demo with and without its AgentHub skill in disposable directories.
# Usage: demos/run.sh OUT_DIR [RUNS]   (needs Claude Code on PATH; read-only tools only)
# Every run gets an empty CLAUDE_CONFIG_DIR, so user-level instructions (CLAUDE.md), memory, plugins and MCP servers
# of the host cannot influence either condition. Model access must come from the environment (e.g. ANTHROPIC_*).
set -euo pipefail
OUT=${1:?usage: demos/run.sh OUT_DIR [RUNS]}
RUNS=${2:-3}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT/raw"
for demo in shell migration review; do
  skill=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["demos"][sys.argv[2]]["skill"])' "$ROOT/demos/rubric.json" "$demo")
  prompt=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["demos"][sys.argv[2]]["prompt"])' "$ROOT/demos/rubric.json" "$demo")
  for condition in baseline skill; do
    for run in $(seq 1 "$RUNS"); do
      ws="$WORK/$demo-$condition-$run"
      mkdir -p "$ws"
      cp -R "$ROOT/demos/fixtures/$demo/." "$ws/"
      if [ "$condition" = skill ]; then
        python3 "$ROOT/cli/xah.py" add "$skill" --agent claude --target "$ws" >/dev/null
      fi
      mkdir -p "$WORK/config-$demo-$condition-$run"
      (cd "$ws" && CLAUDE_CONFIG_DIR="$WORK/config-$demo-$condition-$run" timeout 600 claude -p "$prompt" --output-format stream-json --verbose \
        --allowedTools "Read,Glob,Grep,Skill" --disallowedTools "Bash,Write,Edit,WebFetch,WebSearch" \
        > "$OUT/raw/$demo-$condition-$run.jsonl" 2>/dev/null) || echo "$demo-$condition-$run: exit $?" >&2
      echo "$demo-$condition-$run done"
    done
  done
done
