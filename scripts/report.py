#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Render the appendix of REPORT.md -- every built context's measured summary, findings and
decisions -- from each context's concepts.yml and profile.yml (and, for the early contexts
whose README is hand-written, its Decisions section). Generated, so it cannot drift from the
files it reports on. The narrative above the marker is written by hand."""
import glob, re
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
out = []
for c in yaml.safe_load(open(HUB / "contexts.yml"))["contexts"]:
    if c["status"] == "planned":
        continue
    repo = HUB.parent / c["context"]
    cfg = yaml.safe_load(open(repo / "concepts.yml"))
    prof = yaml.safe_load(open(repo / "profile.yml"))
    n_cw = len(glob.glob(str(repo / "crosswalk" / "*.yml")))
    out.append(f"### {c['name']} (`{c['context']}`)\n")
    where = (f"[api-commons/{c['context']}](https://github.com/api-commons/{c['context']})" if c.get("repo")
             else f"measured and recorded as `{c['status']}`, not published")
    out.append(f"{prof['cohort']['providers_with_harvested_openapi']} providers measured, {n_cw} crosswalks, {where}.\n")
    if prof.get("kind") == "reference":
        out.append(f"- reference context for `{prof['standard']}`: {prof['implementers']} providers implement it, "
                   f"{prof.get('mentioned_by', 0)} name it")
        for api, v in prof["apis"].items():
            out.append(f"  - `{api}` ({v['providers']} implementers)")
    for name, v in (prof.get("concepts") or {}).items():
        core = [p["name"] for p in v["properties"] if p["tier"] == "core"]
        out.append(f"- `{name}` ({v['providers_exposing']} providers): "
                   + (", ".join(f"`{x}`" for x in core) if core else "no core"))
    out.append("")
    findings = cfg.get("findings") or []
    decisions = [" ".join(d.split()) for d in cfg.get("decisions") or []]
    if not decisions:  # early contexts: decisions live in the hand-written README
        text = (repo / "README.md").read_text()
        m = re.search(r"## Decisions\n(.*?)\n## ", text, re.S)
        if m:
            decisions = [" ".join(b.split()) for b in re.split(r"\n- ", "\n" + m.group(1)) if b.strip().startswith("**")]
    if findings:
        out.append("Findings:\n")
        out += [f"- {' '.join(f.split())}" for f in findings]
        out.append("")
    if decisions:
        out.append("Decisions:\n")
        out += [f"- {d}" for d in decisions]
        out.append("")
report = HUB / "REPORT.md"
text = report.read_text()
marker = "<!-- report:appendix -->"
report.write_text(text[: text.index(marker) + len(marker)] + "\n\n" + "\n".join(out) + "\n")
print(len(out), "lines")
