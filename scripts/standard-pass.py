#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure a bounded context against a standard's own definition.

The census measures what providers publish. Some domains have a standard that providers
implement without publishing it as OpenAPI (OCPI, OTLP, CAP, RESO). This reads the standard's
field list (standards/<name>.yml, extracted from its own source) and, for each concept the
context maps to a standard object, records:

  crosswalk       common property -> the standard's field name (the standard as one more voice)
  core_coverage   share of the measured core the standard defines
  standard_only   fields the standard defines that no provider in the cohort publishes at any tier

Run from the context repo. Config in concepts.yml:
  standards:
    - standard: cap-1.2
      concepts: {weather_alert: [alert, info]}
      defines: {location: Location}      # optional: objects for concepts the market did not publish
Writes standards/<name>.yml in the context repo."""
import re
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
cfg = yaml.safe_load(open("concepts.yml"))
prof = yaml.safe_load(open("profile.yml"))["concepts"]


def snake(n):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", n))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


Path("standards").mkdir(exist_ok=True)
for entry in cfg.get("standards") or []:
    std = yaml.safe_load(open(HUB / "standards" / f"{entry['standard']}.yml"))
    result = {"standard": entry["standard"], "source": std["source"], "concepts": {}, "defines_unpublished": {}}
    for concept, objs in (entry.get("concepts") or {}).items():
        fields = [f for o in objs for f in std["objects"].get(o, [])]
        alias = {}
        for group in (cfg.get("common_fields") or {}, cfg["concepts"][concept].get("aliases") or {}):
            for canon, al in group.items():
                alias[str(canon)] = str(canon)
                for x in al:
                    alias[snake(str(x))] = str(canon)
        known = {p["name"]: p["tier"] for p in prof[concept]["properties"]}
        long_tail = set(prof[concept].get("long_tail_sample") or [])
        mapping, only = {}, []
        for f in fields:
            canon = alias.get(snake(f), snake(f))
            if canon in known or canon in long_tail:
                mapping.setdefault(canon, f)
            else:
                only.append(f)
        core = [n for n, t in known.items() if t == "core"]
        ext = [n for n, t in known.items() if t == "extended"]
        result["concepts"][concept] = {
            "objects": objs,
            "core_coverage": round(sum(1 for c in core if c in mapping) / len(core), 3) if core else None,
            "extended_coverage": round(sum(1 for c in ext if c in mapping) / (len(ext) or 1), 3),
            "core_missing_from_standard": [c for c in core if c not in mapping],
            "crosswalk": mapping,
            "standard_only": only,
        }
    for concept, obj in (entry.get("defines") or {}).items():
        result["defines_unpublished"][concept] = {"object": obj, "fields": std["objects"].get(obj, [])}
    yaml.safe_dump(result, open(f"standards/{entry['standard']}.yml", "w"), sort_keys=False, width=110)
    for c, r in result["concepts"].items():
        print(f"{entry['standard']} -> {c}: core {('n/a' if r['core_coverage'] is None else format(r['core_coverage'], '.0%'))}, extended {r['extended_coverage']:.0%}, "
              f"{len(r['standard_only'])} standard-only fields; core not in standard: {r['core_missing_from_standard']}")
