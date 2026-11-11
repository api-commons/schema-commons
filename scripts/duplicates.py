#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Report catalog listings that are probably one company: providers in a context's cohort
whose harvested OpenAPI files are byte-identical. Run from the context repo after
cohort.py. It only REPORTS -- a person decides, and writes the merge under `duplicates:`
in concepts.yml (same company) or leaves it (a reseller republishing a vendor's spec is a
different provider)."""
import collections, hashlib, json, sys
from pathlib import Path
import yaml

ALL = Path("/Users/kinlane/Github/all")
cfg = yaml.safe_load(open("concepts.yml"))
known = {d for ds in (cfg.get("duplicates") or {}).values() for d in ds} | set(cfg.get("duplicates") or {})
by_hash = collections.defaultdict(set)
for c in json.load(open("census/cohort.json")):
    for rel in c["specs"]:
        try:
            by_hash[hashlib.sha256((ALL / c["slug"] / rel).read_bytes()).hexdigest()].add(c["slug"])
        except OSError:
            pass
groups = {frozenset(s) for s in by_hash.values() if len(s) > 1}
for g in sorted(groups, key=lambda g: sorted(g)):
    flag = "  (already merged)" if set(g) <= known else ""
    print(" = ".join(sorted(g)) + flag)
print(f"{len(groups)} candidate groups", file=sys.stderr)
