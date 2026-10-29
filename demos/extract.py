#!/usr/bin/env python3
"""Turn raw Claude Code stream-json traces into committed results: the final answer and metrics per run.

Raw traces stay out of git (they contain host-specific session metadata). Usage: extract.py RAW_DIR OUT_DIR
"""
import json
import pathlib
import sys


def extract(trace):
    skills, sources, tools, result, init = [], [], [], {}, {}
    for line in trace.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = event
        if event.get("type") == "user":
            for part in event["message"].get("content", []) if isinstance(event["message"].get("content"), list) else []:
                text = json.dumps(part)
                if "Base directory for this skill:" in text:
                    sources.append("project" if "/.claude/skills/" in text else "other")
        if event.get("type") == "assistant":
            for part in event["message"].get("content", []):
                if part.get("type") == "tool_use":
                    tools.append(part["name"])
                    if part["name"] == "Skill":
                        skills.append(part["input"].get("skill") or part["input"].get("command", ""))
        if event.get("type") == "result":
            result = event
    usage = result.get("usage", {})
    return result.get("result", ""), {
        "skill_calls": skills,
        "skill_sources": sources,
        "client": init.get("claude_code_version"),
        "model": init.get("model"),
        "mcp_servers": len(init.get("mcp_servers") or []),
        "tool_calls": len(tools),
        "turns": result.get("num_turns"),
        "duration_s": round((result.get("duration_ms") or 0) / 1000, 1),
        "output_tokens": usage.get("output_tokens"),
        "cost_usd": round(result.get("total_cost_usd") or 0, 4),
        "is_error": result.get("is_error", True),
    }


def main(raw_dir, out_dir):
    out = pathlib.Path(out_dir)
    (out / "answers").mkdir(parents=True, exist_ok=True)
    metrics = {}
    for trace in sorted(pathlib.Path(raw_dir).glob("*.jsonl")):
        answer, metrics[trace.stem] = extract(trace)
        (out / "answers" / f"{trace.stem}.txt").write_text(answer.strip() + "\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"extracted {len(metrics)} run(s) into {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
