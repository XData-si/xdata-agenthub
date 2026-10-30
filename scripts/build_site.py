#!/usr/bin/env python3
"""Build the static catalog site (site/index.html) from registry/catalog.json. Standard library only."""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from mcp_catalog import LEVEL_LABELS

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
    seals_path = ROOT / "registry/seals.json"
    seals = json.loads(seals_path.read_text(encoding="utf-8"))["seals"] if seals_path.is_file() else {}
    labels = {"reviewed": "XData Reviewed", "verified": "XData Verified", "eu-ready": "EU Ready"}
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
                + "".join(f'<span class="seal seal-{s["level"]}">{labels.get(s["level"], s["level"])}</span>'
                          for s in seals.get(item["id"], []))
                +
                f'<p>{description}</p>'
                f'<code>python3 cli/xah.py add {skill_id} --agent claude --scope user</code>'
                '</article>')
    mcp_path = ROOT / "registry/mcp-servers.json"
    servers = json.loads(mcp_path.read_text(encoding="utf-8"))["servers"] if mcp_path.is_file() else []
    if servers:
        cards.append('<h2 data-section id="mcp">MCP servers (preview)</h2>'
                     '<p class="note">Listed servers are metadata from the official MCP Registry, pinned to one '
                     'version. <b>L0 means listed only: not reviewed, scanned or tested.</b> '
                     f'<a href="{REPO}/blob/main/docs/VERIFIED_MCP.md">Verification levels</a></p>')
    for server in servers:
        title = html.escape(server.get("title", server["id"]))
        name = html.escape(server["name"])
        description = html.escape(server["description"])
        level = html.escape(server["level"])
        transport = html.escape(", ".join(sorted({a["transport"] for a in server["artifacts"]})))
        link = html.escape(server.get("repository") or server.get("website") or "")
        heading = f'<a href="{link}" rel="noopener">{title}</a>' if link else title
        cards.append(
            f'<article data-text="mcp {html.escape(server["id"])} {name.lower()} {description.lower()}">'
            f'<h3>{heading}</h3>'
            f'<span class="seal seal-mcp-{level.lower()}">{level} {LEVEL_LABELS[server["level"]]}</span>'
            f'<p>{description}</p>'
            f'<code>{name} {html.escape(server["version"])} · {transport}</code>'
            '</article>')
    levels = [s["level"] for item in skills for s in seals.get(item["id"], [])]
    page = (TEMPLATE.replace("{{COUNT}}", str(len(skills))).replace("{{CARDS}}", "\n".join(cards))
            .replace("{{REVIEWED}}", str(levels.count("reviewed"))).replace("{{EU}}", str(levels.count("eu-ready")))
            .replace("{{VERIFIED}}", str(levels.count("verified"))))
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
<meta name="description" content="{{COUNT}} curated, security-reviewed agent skills for Claude Code, Codex, OpenCode and other Agent Skills clients.">
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
.seal{display:inline-block;font-size:.72rem;font-weight:600;padding:2px 8px;border-radius:999px;margin:0 4px 6px 0;border:1px solid var(--line)}
.seal-verified{color:#15803d;border-color:#15803d}.seal-reviewed{color:var(--accent);border-color:var(--accent)}.seal-eu-ready{color:#1d4ed8;border-color:#facc15;background:rgba(250,204,21,.12)}
.seal-mcp-l0{color:var(--muted)}.note{grid-column:1/-1;margin:0;color:var(--muted);font-size:.92rem}
article p{margin:0 0 8px;color:var(--muted);font-size:.92rem}a{color:var(--accent)}footer{color:var(--muted);text-align:center;padding:32px 16px}

.hero{position:relative;overflow:hidden;color:#e2e8f0;background:radial-gradient(1200px 500px at 80% -10%,rgba(124,58,237,.45),transparent 60%),radial-gradient(900px 500px at 0% 110%,rgba(37,99,235,.40),transparent 60%),linear-gradient(160deg,#060b18 0%,#0b1120 55%,#111b3a 100%)}
.hero::before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(148,163,184,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,184,.08) 1px,transparent 1px);background-size:44px 44px;mask-image:radial-gradient(ellipse at 60% 40%,#000 30%,transparent 75%);animation:drift 30s linear infinite}
@keyframes drift{to{background-position:44px 44px,44px 44px}}
.hero-in{position:relative;max-width:1100px;margin:0 auto;padding:56px 16px 48px;display:grid;grid-template-columns:1.15fr .85fr;gap:32px;align-items:center}
@media (max-width:860px){.hero-in{grid-template-columns:1fr}.hero-art{max-width:360px;margin:0 auto}}
.brand{display:flex;align-items:center;gap:10px;font-weight:600;color:#cbd5e1}.brand img{width:36px;height:36px}
.eyebrow{display:inline-block;margin:18px 0 10px;padding:4px 12px;border:1px solid rgba(250,204,21,.5);border-radius:999px;color:#fde68a;font-size:.8rem;background:rgba(250,204,21,.08)}
.hero h1{font-size:clamp(2.1rem,5vw,3.4rem);line-height:1.08;margin:0 0 14px;letter-spacing:-.02em}
.hero h1 span{background:linear-gradient(90deg,#60a5fa,#a78bfa,#f0abfc);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p.lead{font-size:1.12rem;color:#cbd5e1;margin:0 0 22px;max-width:40ch}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:26px}
.btn{display:inline-block;padding:11px 18px;border-radius:10px;font-weight:600;text-decoration:none;transition:transform .15s,box-shadow .15s}
.btn:hover{transform:translateY(-1px)}.btn-primary{background:linear-gradient(90deg,#2563eb,#7c3aed);color:#fff;box-shadow:0 8px 24px rgba(79,70,229,.35)}
.btn-ghost{color:#e2e8f0;border:1px solid rgba(148,163,184,.4);background:rgba(15,23,42,.4)}
.stats{display:flex;flex-wrap:wrap;gap:22px}.stat b{display:block;font-size:1.7rem;color:#fff}.stat span{font-size:.82rem;color:#94a3b8}
.hero-art svg{width:100%;height:auto;display:block}
.orbit{transform-origin:200px 200px;animation:spin 60s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.link{stroke-dasharray:4 6;animation:flow 2.4s linear infinite}@keyframes flow{to{stroke-dashoffset:-20}}
.pulse{animation:pulse 3s ease-in-out infinite;transform-origin:200px 200px}@keyframes pulse{50%{opacity:.35;transform:scale(1.08)}}
@media (prefers-reduced-motion:reduce){.hero::before,.orbit,.link,.pulse{animation:none}}
.pipeline{max-width:1100px;margin:-26px auto 0;padding:0 16px;position:relative}
.steps{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 10px 30px rgba(2,6,23,.18)}
@media (max-width:760px){.steps{grid-template-columns:1fr 1fr}}
.step{display:flex;gap:10px;align-items:flex-start;font-size:.88rem;color:var(--muted)}.step b{display:block;color:var(--fg);font-size:.92rem}
.step i{flex:none;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-style:normal;font-weight:700;color:#fff;background:linear-gradient(135deg,#2563eb,#7c3aed)}
.installs{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:28px 0 16px}
.installs .install{margin:0}.install h3{margin:0 0 8px;font-size:1rem}
</style>
<!-- Umami web analytics (self-hosted, cookieless) -->
<script defer src="https://analytics2.xdata.si/script.js" data-website-id="527ddb63-6a19-4654-8038-3b1885e82490"></script>
<script defer src="https://analytics2.xdata.si/recorder.js" data-website-id="527ddb63-6a19-4654-8038-3b1885e82490"></script>
</head>
<body>
<section class="hero"><div class="hero-in">
<div>
<div class="brand"><img src="logo.svg" alt="">XData AgentHub</div>
<div class="eyebrow">Made in the EU · Open source · MIT</div>
<h1>Agent skills <span>you can trust</span></h1>
<p class="lead">{{COUNT}} curated skills for Claude Code, Codex, OpenCode and any Agent Skills client — every one security-reviewed, sealed and signed. Instructions only, no bundled scripts.</p>
<div class="cta"><a class="btn btn-primary" href="#catalog">Browse skills</a><a class="btn btn-ghost" href="#install">Install</a><a class="btn btn-ghost" href="https://github.com/XData-si/xdata-agenthub/blob/main/CONTRIBUTING.md">Contribute a skill</a></div>
<div class="stats"><div class="stat"><b>{{COUNT}}</b><span>skills</span></div><div class="stat"><b>{{REVIEWED}}</b><span>security-reviewed</span></div><div class="stat"><b>{{EU}}</b><span>EU Ready</span></div><div class="stat"><b>{{VERIFIED}}</b><span>runtime-verified</span></div></div>
</div>
<div class="hero-art" aria-hidden="true">
<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#7c3aed" stop-opacity=".55"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
<linearGradient id="core" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs>
<circle class="pulse" cx="200" cy="200" r="150" fill="url(#glow)"/>
<circle cx="200" cy="200" r="132" fill="none" stroke="rgba(148,163,184,.25)" stroke-dasharray="2 8"/>
<g class="orbit">
<g stroke="#93c5fd" stroke-width="1.5" fill="none" opacity=".8">
<line class="link" x1="200" y1="200" x2="200" y2="68"/><line class="link" x1="200" y1="200" x2="326" y2="159"/><line class="link" x1="200" y1="200" x2="278" y2="307"/><line class="link" x1="200" y1="200" x2="122" y2="307"/><line class="link" x1="200" y1="200" x2="74" y2="159"/>
</g>
<g font-family="system-ui,sans-serif" font-size="11" font-weight="600" text-anchor="middle" fill="#e2e8f0">
<circle cx="200" cy="68" r="26" fill="#0f172a" stroke="#60a5fa" stroke-width="2"/><text x="200" y="72">AI</text>
<circle cx="326" cy="159" r="26" fill="#0f172a" stroke="#a78bfa" stroke-width="2"/><text x="326" y="163">Security</text>
<circle cx="278" cy="307" r="26" fill="#0f172a" stroke="#f0abfc" stroke-width="2"/><text x="278" y="311">DevOps</text>
<circle cx="122" cy="307" r="26" fill="#0f172a" stroke="#facc15" stroke-width="2"/><text x="122" y="311">EU</text>
<circle cx="74" cy="159" r="26" fill="#0f172a" stroke="#34d399" stroke-width="2"/><text x="74" y="156">Engi-</text><text x="74" y="169">neering</text>
</g></g>
<circle cx="200" cy="200" r="46" fill="url(#core)"/>
<path d="M183 201l11 11 23-25" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div>
</div></section>
<section class="pipeline"><div class="steps">
<div class="step"><i>1</i><div><b>Security gate</b>no scripts, hidden text or injection</div></div>
<div class="step"><i>2</i><div><b>AI review</b>unsafe advice, missing approvals</div></div>
<div class="step"><i>3</i><div><b>Maintainer review</b>accuracy and quality</div></div>
<div class="step"><i>4</i><div><b>Seal</b>bound to the skill's digest</div></div>
<div class="step"><i>5</i><div><b>Signed release</b>Sigstore + SLSA provenance</div></div>
</div></section>
<main>
<div class="installs" id="install">
<section class="install"><h3>Claude Code</h3><code>/plugin marketplace add XData-si/xdata-agenthub</code><code>/plugin install xdata-agenthub@xdata-agenthub</code></section>
<section class="install"><h3>Any agent (Codex, OpenCode …)</h3><code>git clone https://github.com/XData-si/xdata-agenthub</code><code>python3 xdata-agenthub/cli/xah.py add &lt;skill&gt; --agent codex --scope user</code></section>
<section class="install"><h3>Contribute</h3><p>Your skill goes through the same security review and gets the same seal. <a href="https://github.com/XData-si/xdata-agenthub/blob/main/CONTRIBUTING.md">How to contribute</a> · <a href="https://github.com/XData-si/xdata-agenthub/blob/main/docs/SEAL.md">How seals work</a></p></section>
</div>
<h2 id="catalog" style="margin-top:8px">Catalog</h2>
<input id="q" type="search" placeholder="Filter skills and MCP servers (e.g. oauth, migration, rag, mcp)" aria-label="Filter skills and MCP servers">
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
while(n&&n.tagName!=='H2'){if(n.tagName==='ARTICLE'&&!n.hidden)any=true;n=n.nextElementSibling}h.hidden=!any;
if(h.nextElementSibling&&h.nextElementSibling.classList.contains('note'))h.nextElementSibling.hidden=!any});});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site"
    print(f"Built {target / 'index.html'} with {build(target)} skills")
