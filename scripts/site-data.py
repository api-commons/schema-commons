#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Write _data/schema_commons.yml for the API Commons site (apicommons.org/schemas/): every
built and reference context with its repository and measured numbers, and the totals.
Generated from contexts.yml and each context's profile, so the page cannot drift.

Usage: site-data.py <path to the api-commons site checkout>"""
import sys
from datetime import date
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
COMMONS = HUB.parent
out = Path(sys.argv[1]) / "_data" / "schema_commons.yml"
GH = "https://github.com/api-commons"

built, references, thin = [], [], 0
providers = set()
for c in yaml.safe_load(open(HUB / "contexts.yml"))["contexts"]:
    repo = COMMONS / c["context"]
    if c["status"] == "thin":
        thin += 1
        continue
    if c["status"] not in ("built", "published", "reference"):
        continue
    cfg = yaml.safe_load(open(repo / "concepts.yml"))
    prof = yaml.safe_load(open(repo / "profile.yml"))
    crosswalks = list((repo / "crosswalk").glob("*.yml"))
    providers |= {p.stem for p in crosswalks}
    row = {"context": c["context"], "name": cfg["name"], "repo": f"{GH}/{c['context']}",
           "measured": prof["cohort"]["providers_with_harvested_openapi"]}
    if c["status"] == "reference":
        row.update({"standard": cfg["reference"]["standard"], "home": cfg["reference"]["home"],
                    "implementers": prof["implementers"], "mentioned_by": prof.get("mentioned_by", 0)})
        references.append(row)
    else:
        row.update({"concepts": [k for k in prof["concepts"]],
                    "core": sum(1 for v in prof["concepts"].values() for p in v["properties"] if p["tier"] == "core"),
                    "crosswalks": len(crosswalks),
                    "version": (cfg.get("release") or {}).get("version") or "draft",
                    "standards": [p.stem for p in sorted((repo / "standards").glob("*.yml"))]
                    if (repo / "standards").exists() else []})
        built.append(row)

data = {"generated": date.today().isoformat(), "hub": f"{GH}/schema-commons",
        "report": f"{GH}/schema-commons/blob/main/REPORT.md",
        "standards_registry": f"{GH}/schema-commons/blob/main/standards/README.md",
        "ruleset": "https://github.com/openlint/rules",
        "totals": {"measured": len(built) + len(references) + thin, "built": len(built),
                   "references": len(references), "thin": thin,
                   "concepts": sum(len(b["concepts"]) for b in built), "core": sum(b["core"] for b in built),
                   "crosswalks": sum(b["crosswalks"] for b in built), "providers": len(providers)},
        "contexts": sorted(built, key=lambda b: b["name"].lower()),
        "references": references}
yaml.safe_dump(data, open(out, "w"), sort_keys=False, width=200, allow_unicode=True)
print(f"wrote {out}: {len(built)} contexts, {len(references)} reference contexts, {thin} thin")
