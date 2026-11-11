#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure the naming conventions the naming ruleset cites, across every built context.

Reads each context's census/census.json (listed in contexts.yml) and counts PROVIDERS per
convention, union across contexts, with catalog duplicates folded into one company.
Writes evidence/naming.yml. The numbers in the ruleset's rule descriptions are copied from
this file; re-run it whenever a context is added or rebuilt, then update the ruleset."""
import collections, json, re
from datetime import date
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
ctxs = [c for c in yaml.safe_load(open(HUB / "contexts.yml"))["contexts"] if c["status"] != "planned"]


def snake(n):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", n))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


m = collections.defaultdict(lambda: collections.defaultdict(set))
cohort = set()
for c in ctxs:
    repo = HUB.parent / c["context"]
    cfg = yaml.safe_load(open(repo / "concepts.yml"))
    dup = {d: k for k, ds in (cfg.get("duplicates") or {}).items() for d in ds}
    census = json.load(open(repo / "census" / "census.json"))
    cohort |= {dup.get(x["slug"], x["slug"]) for x in json.load(open(repo / "census" / "cohort.json"))}
    for dim, vals in census["naming"].items():
        for v, slugs in vals.items():
            m[dim][v] |= {dup.get(s, s) for s in slugs}
    for concept, provs in census["concepts"].items():
        for s, h in provs.items():
            s = dup.get(s, s)
            for seg in h["segments"]:
                m["collection_noun"]["plural" if seg.endswith("s") else "singular"].add(s)
            for n in h["properties"]:
                sn = snake(n)
                if re.match(r"^(created|updated|modified)", sn) or re.match(r"^(add|update|create|modify)_?time$", sn):
                    form = "_at" if sn.endswith("_at") else "_date/_time/on" if re.search(r"(date|time|on)$", sn) else "bare"
                    m["timestamp"][form].add(s)
                if n not in ("id", "ID") and re.search(r"(Id|ID|_id)$", n):
                    m["foreign_key"]["_id" if n.endswith("_id") else "Id"].add(s)

out = {"generated": date.today().isoformat(), "contexts": [c["context"] for c in ctxs],
       "providers": len(cohort),
       "note": "Counts are providers (catalog duplicates folded), a provider can appear under several forms.",
       "measures": {dim: {v: len(s) for v, s in sorted(vals.items(), key=lambda kv: -len(kv[1]))}
                    for dim, vals in sorted(m.items())}}
yaml.safe_dump(out, open(HUB / "evidence" / "naming.yml", "w"), sort_keys=False)
print(yaml.safe_dump(out["measures"], sort_keys=False))
print(out["providers"], "providers across", out["contexts"])
