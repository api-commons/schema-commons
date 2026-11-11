#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""List the matches a person has to look at: every provider counted for a concept ONLY
through a segment outside that concept's first two (its unambiguous names), with a sample
of its properties and the path that matched. Run from the context repo after census.py.
Usage: review.py [--max N]"""
import argparse, json
import yaml

ap = argparse.ArgumentParser()
ap.add_argument("--max", type=int, default=40)
a = ap.parse_args()
cfg = yaml.safe_load(open("concepts.yml"))
census = json.load(open("census/census.json"))
ex = cfg.get("exclude") or {}
for concept, spec in cfg["concepts"].items():
    primary = {s.split("@")[0].split("!")[0] for s in spec["segments"][:2]}
    rows = []
    for slug, h in census["concepts"].get(concept, {}).items():
        if slug in (ex.get(concept) or {}) or set(h["segments"]) & primary:
            continue
        ev = h["evidence"][0].split("#", 1)[1] if h["evidence"] else ""
        rows.append(f"  {slug} {h['segments'][:2]} {sorted(h['properties'])[:7]} {ev[:70]}")
    if rows:
        print(f"{concept}: {len(rows)} via secondary segments")
        print("\n".join(rows[:a.max]))
