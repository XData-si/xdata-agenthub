#!/usr/bin/env python3
"""Score committed demo answers against the pre-registered rubric (demos/rubric.json).

Usage: score.py RESULTS_DIR [--overrides FILE] [--markdown]
Overrides record maintainer corrections where a pattern missed or wrongly matched an item:
{"<run>": {"<item>": true|false, "reason": "..."}}. They are listed in the output so nothing is hidden.
"""
import json
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def score(results_dir, overrides=None):
    rubric = json.loads((ROOT / "rubric.json").read_text(encoding="utf-8"))["demos"]
    metrics = json.loads((results_dir / "metrics.json").read_text(encoding="utf-8"))
    overrides = overrides or {}
    runs = {}
    for answer_file in sorted((results_dir / "answers").glob("*.txt")):
        run = answer_file.stem
        demo = run.split("-")[0]
        text = answer_file.read_text(encoding="utf-8")
        found = {item: any(re.search(p, text, re.I) for p in patterns)
                 for item, patterns in rubric[demo]["items"].items()}
        for item, value in overrides.get(run, {}).items():
            if item in found:
                found[item] = value
        runs[run] = {"demo": demo, "condition": run.split("-")[1], "found": found, **metrics.get(run, {})}
    return rubric, runs


def summary(rubric, runs):
    rows = []
    for demo, spec in rubric.items():
        for condition in ("baseline", "skill"):
            group = [r for r in runs.values() if r["demo"] == demo and r["condition"] == condition]
            if not group:
                continue
            total = len(spec["items"])
            hits = [sum(r["found"].values()) for r in group]
            per_item = {item: sum(r["found"][item] for r in group) for item in spec["items"]}
            rows.append({
                "demo": demo, "condition": condition, "runs": len(group), "items": total,
                "found_mean": round(statistics.mean(hits), 2), "found_min": min(hits), "found_max": max(hits),
                "per_item": per_item,
                "skill_loaded": sum(1 for r in group if r.get("skill_calls")),
                "duration_s_mean": round(statistics.mean(r.get("duration_s") or 0 for r in group), 1),
                "cost_usd_mean": round(statistics.mean(r.get("cost_usd") or 0 for r in group), 4),
            })
    return rows


def markdown(rubric, rows):
    lines = ["| Demo | Condition | Runs | Items found (mean, min–max) | Skill loaded | Mean time | Mean cost |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['demo']} | {r['condition']} | {r['runs']} | {r['found_mean']}/{r['items']} "
                     f"({r['found_min']}–{r['found_max']}) | {r['skill_loaded']}/{r['runs']} | "
                     f"{r['duration_s_mean']} s | ${r['cost_usd_mean']} |")
    for demo, spec in rubric.items():
        lines += ["", f"**{demo}** — runs that found each item (baseline / skill):", ""]
        group = {r["condition"]: r for r in rows if r["demo"] == demo}
        for item in spec["items"]:
            b = group.get("baseline", {}).get("per_item", {}).get(item, "–")
            s = group.get("skill", {}).get("per_item", {}).get(item, "–")
            lines.append(f"- {item}: {b} / {s}")
    return "\n".join(lines)


def main(argv):
    results_dir = pathlib.Path(argv[0])
    overrides = {}
    if "--overrides" in argv:
        overrides = json.loads(pathlib.Path(argv[argv.index("--overrides") + 1]).read_text(encoding="utf-8"))
    rubric, runs = score(results_dir, overrides)
    rows = summary(rubric, runs)
    if "--markdown" in argv:
        print(markdown(rubric, rows))
    else:
        print(json.dumps({"summary": rows, "runs": runs}, indent=2))
    for run, items in overrides.items():
        for item, value in items.items():
            if item != "reason":
                print(f"override {run}: {item} = {value} ({items.get('reason', '')})", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
