#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Render standards/README.md: every standard the commons reads, where it came from, and which
contexts it serves -- as a measuring stick (a census context's `standards:` block) or as the
owner of the shape (a reference context's `reference:` block). Thin contexts that name a
standard as the route forward are listed as candidates. Generated; do not edit the README."""
import re
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
COMMONS = HUB.parent
registry = yaml.safe_load(open(HUB / "contexts.yml"))["contexts"]

measured, owns = {}, {}
for c in registry:
    if c["status"] in ("planned", "thin"):
        continue
    cfg = yaml.safe_load(open(COMMONS / c["context"] / "concepts.yml"))
    for s in cfg.get("standards") or []:
        measured.setdefault(s["standard"], []).append(c["context"])
    if cfg.get("reference"):
        owns.setdefault(cfg["reference"]["standard"], []).append(c["context"])

rows = ["| Standard | Source | Measures | Owns the shape of |", "| --- | --- | --- | --- |"]
for f in sorted((HUB / "standards").glob("*.yml")):
    s = yaml.safe_load(open(f))
    name = s["standard"]
    src = s["source"] if s["source"].startswith("http") else s["source"]
    link = re.match(r"(https?://\S+)", src)
    src_md = f"[{link.group(1).split('//')[1].split('/')[0]}]({link.group(1)})" if link else src
    ctx = lambda xs: ", ".join(f"[{x}](https://github.com/api-commons/{x})" for x in xs) or "--"
    rows.append(f"| `{name}` ({len(s['objects'])} objects) | {src_md} | {ctx(measured.get(name, []))} | "
                f"{ctx(owns.get(name, []))} |")

# Thin contexts whose findings point to a standard: the queue of standards passes.
cands = []
for c in registry:
    if c["status"] != "thin":
        continue
    rec = HUB / "thin" / c["context"] / "concepts.yml"
    if not rec.exists():
        continue
    text = " ".join(yaml.safe_load(open(rec)).get("findings") or [])
    if re.search(r"standard|reference", text, re.I):
        cands.append(f"- **{c['name']}** (`{c['context']}`): {' '.join(text.split())}")

out = ["# Standards", "",
       "Every standard Schema Commons reads, extracted from the standard's own published source by "
       "`scripts/extract-standard.py` (nothing here comes from a provider's spec). A standard serves a "
       "context in one of two ways:", "",
       "- **Measures** -- a census context's core is compared with the standard's objects, and the README "
       "shows the coverage both ways (`scripts/standard-pass.py`).",
       "- **Owns the shape** -- a reference context publishes the standard's objects unchanged and measures "
       "which providers implement them (`scripts/reference.py`).", "", *rows, "",
       "## Candidates", "",
       "Thin contexts whose findings name a standard as the route forward, each one a standards pass "
       "waiting to be run:", "", *cands, ""]
(HUB / "standards" / "README.md").write_text("\n".join(out))
print(f"{len(rows) - 2} standards, {len(cands)} candidates")
