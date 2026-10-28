#!/usr/bin/env python3
"""Build the static catalog site (site/index.html) from registry/catalog.json. Standard library only."""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "https://github.com/XData-si/xdata-agenthub"


def sections():
    """Map skill id -> catalog section title from docs/CATALOG.md."""
    result = {}
    text = (ROOT / "docs/CATALOG.md").read_text(encoding="utf-8")
    for block in re.split(r"\n## ", text)[1:]:
        title = block.splitlines()[0].strip()
        for skill_id in re.findall(r"^- `([a-z0-9-]+)`", block, re.M):
            result[skill_id] = title
    return result


def skill_description(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    match = re.search(r"(?m)^description:\s*(.+)$", text.split("---", 2)[1])
    return match.group(1).strip() if match else ""


def build(out_dir):
    catalog = json.loads((ROOT / "registry/catalog.json").read_text(encoding="utf-8"))
    section_of = sections()
    skills = [item for item in catalog["items"] if item["type"] == "skill"]
    order = list(dict.fromkeys(section_of.values()))
    cards = []
    for title in order:
        cards.append(f'<h2 data-section>{html.escape(title)}</h2>')
        for item in sorted((s for s in skills if section_of.get(s["id"]) == title), key=lambda s: s["id"]):
            skill_id = html.escape(item["id"])
            description = html.escape(skill_description(item["path"]))
            cards.append(
                f'<article data-text="{skill_id} {description.lower()}">'
                f'<h3><a href="{REPO}/blob/main/{html.escape(item["path"])}">{skill_id}</a></h3>'
                f'<p>{description}</p>'
                f'<code>python3 cli/xah.py add {skill_id} --agent claude --scope user</code>'
                '</article>')
    page = TEMPLATE.replace("{{COUNT}}", str(len(skills))).replace("{{CARDS}}", "\n".join(cards))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    (out_dir / "catalog.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logo = ROOT / "docs/assets/logo.svg"
    if logo.is_file():
        (out_dir / "logo.svg").write_bytes(logo.read_bytes())
    return len(skills)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>XData AgentHub — curated agent skills</title>
<meta name="description" content="{{COUNT}} curated, security-first agent skills for Claude Code, Codex, OpenCode and other Agent Skills clients.">
<link rel="icon" href="logo.svg">
<style>
:root{--bg:#f8fafc;--fg:#0f172a;--muted:#475569;--card:#fff;--line:#e2e8f0;--accent:#2563eb}
@media (prefers-color-scheme:dark){:root{--bg:#0b1120;--fg:#e2e8f0;--muted:#94a3b8;--card:#111827;--line:#1f2937;--accent:#60a5fa}}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--fg)}
header,main{max-width:1100px;margin:0 auto;padding:24px 16px}header{display:flex;gap:16px;align-items:center}
header img{width:56px;height:56px}h1{margin:0;font-size:1.8rem}header p{margin:4px 0 0;color:var(--muted)}
.install{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:16px}
.install code,article code{display:block;white-space:pre-wrap;word-break:break-all;font-size:.82rem;color:var(--muted)}
input{width:100%;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);font-size:1rem}
h2{grid-column:1/-1;margin:28px 0 0;font-size:1.1rem}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
article{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}article h3{margin:0 0 6px;font-size:1rem}
article p{margin:0 0 8px;color:var(--muted);font-size:.92rem}a{color:var(--accent)}footer{color:var(--muted);text-align:center;padding:32px 16px}
</style>
</head>
<body>
<header><img src="logo.svg" alt=""><div><h1>XData AgentHub</h1>
<p>{{COUNT}} curated, security-first skills for Claude Code, Codex, OpenCode and any <a href="https://agentskills.io/specification">Agent Skills</a> client. Instructions only — no bundled scripts.</p></div></header>
<main>
<section class="install"><strong>Install</strong>
<code>/plugin marketplace add XData-si/xdata-agenthub</code>
<code>/plugin install xdata-agenthub@xdata-agenthub</code>
<code>git clone https://github.com/XData-si/xdata-agenthub &amp;&amp; python3 xdata-agenthub/cli/xah.py list</code>
<p><a href="https://github.com/XData-si/xdata-agenthub">Source, documentation and contribution guide on GitHub</a></p></section>
<input id="q" type="search" placeholder="Filter skills (e.g. oauth, migration, rag, incident)" aria-label="Filter skills">
<div class="grid">
{{CARDS}}
</div>
</main>
<footer>MIT licensed · maintained by <a href="https://xdata.si">XData</a> · generated from registry/catalog.json</footer>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();
document.querySelectorAll('article').forEach(a=>{a.hidden=v&&!a.dataset.text.includes(v)});
document.querySelectorAll('h2[data-section]').forEach(h=>{let n=h.nextElementSibling,any=false;
while(n&&n.tagName==='ARTICLE'){if(!n.hidden)any=true;n=n.nextElementSibling}h.hidden=!any});});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site"
    print(f"Built {target / 'index.html'} with {build(target)} skills")
