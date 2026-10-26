#!/usr/bin/env python3
"""Regenerate llms.txt, llms-full.txt and registry.json from log/**/*.md"""
import json, re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG  = ROOT / "log"
BASE = "https://YOURNAME.github.io/YOURREPO"   # set this
MAX_FULL_CHARS = 400_000                        # context-window budget

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)

def parse(path):
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    meta, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = text[m.end():]
    return meta, body

entries = []
for p in sorted(LOG.rglob("*.md")):
    meta, body = parse(p)
    rel = p.relative_to(ROOT).as_posix()
    entries.append({
        "id":       meta.get("id", p.stem),
        "date":     meta.get("date", ""),
        "platform": meta.get("platform", "unknown"),
        "model":    meta.get("model", "unknown"),
        "session":  meta.get("session", ""),
        "topic":    meta.get("topic", ""),
        "tags":     [t.strip() for t in meta.get("tags", "").strip("[]").split(",") if t.strip()],
        "url":      f"{BASE}/{rel}",
        "body":     body.strip(),
    })

entries.sort(key=lambda e: (e["date"], e["id"]))

manifest = {
    "generated": datetime.date.today().isoformat(),
    "count": len(entries),
    "entries": [{k: v for k, v in e.items() if k != "body"} for e in entries],
}
(ROOT / "registry.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# llms-full.txt — newest first, capped so it stays ingestible
parts, total = [], 0
for e in reversed(entries):
    chunk = (f"\n\n---\n\n## {e['id']} — {e['topic']}\n\n"
             f"_{e['date']} · {e['platform']} · {e['model']}_\n\n{e['body']}\n")
    if total + len(chunk) > MAX_FULL_CHARS:
        break
    parts.append(chunk); total += len(chunk)

(ROOT / "llms-full.txt").write_text(
    "# Running Log — full text\n\n"
    "> Append-only archive of my conversations with LLM assistants across "
    "platforms, sessions and models, newest first. Machine-readable companion "
    "to /llms.txt.\n" + "".join(parts), encoding="utf-8")

# llms.txt — curated index: H1, blockquote, sections, annotated links
by_platform = {}
for e in entries:
    by_platform.setdefault(e["platform"], []).append(e)

lines = [
    "# Running Log",
    "",
    "> Append-only record of my conversations with LLM assistants across "
    "platforms, sessions and models. Every entry is dated, attributed to a "
    "platform and model, and kept at a permanent URL.",
    "",
    f"Full archive: [{BASE}/llms-full.txt]({BASE}/llms-full.txt)",
    f"Manifest: [{BASE}/registry.json]({BASE}/registry.json)",
    "",
]
for plat, es in sorted(by_platform.items()):
    lines += [f"## {plat}", ""]
    for e in reversed(es[-50:]):
        lines.append(f"- [{e['id']} — {e['topic']}]({e['url']}): {e['date']}, {e['model']}.")
    lines.append("")

(ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"built {len(entries)} entries")
