#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Distill a bounded context's census into its common artifacts.

Run from a context repo (e.g. commons/crm) after census.py. Writes:

  profile.yml            every concept, operation and property with its measured share
  schema/<concept>.json  JSON Schema 2020-12 of the core + extended properties
  openapi.yml            OpenAPI 3.1 of the operations that clear the extended bar
  crosswalk/<slug>.yml   per provider: common name -> the name that provider uses, with
                         the harvested spec it was read from
  adopters.yml           who declares which concept, and to which tier

Tiers are measured, never chosen. Shares are of the providers that expose the concept
with a READABLE resource schema, so a provider whose spec types every body as `object`
neither helps nor hurts a property's share.

  core      declared by at least half of them
  extended  declared by at least a fifth, and by at least three providers
  long tail everything else -- kept in profile.yml, kept out of the schema
"""
import json, re, sys, collections
from datetime import date
from pathlib import Path
import yaml

CORE, EXTENDED, MIN_PROVIDERS = 0.5, 0.2, 3
TODAY = date.today().isoformat()
cfg = yaml.safe_load(open("concepts.yml"))
census = json.load(open("census/census.json"))
CTX = cfg["context"]
RAW = f"https://raw.githubusercontent.com/api-commons/{CTX}/main"
ENVELOPE = set(cfg.get("envelope", []))


def snake(n):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", n))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def tier(share, n):
    if share >= CORE and n >= MIN_PROVIDERS: return "core"
    if share >= EXTENDED and n >= MIN_PROVIDERS: return "extended"
    return "long-tail"


JSON_TYPES = {"string", "integer", "number", "boolean", "object", "array"}
profile = {"context": CTX, "name": cfg["name"], "generated": TODAY,
           "cohort": {"tags": cfg["tags"], "providers_with_harvested_openapi": census["cohort_size"]},
           "thresholds": {"core": CORE, "extended": EXTENDED, "min_providers": MIN_PROVIDERS},
           "concepts": {}}
crosswalks = collections.defaultdict(dict)
adopters = collections.defaultdict(dict)

for concept, spec in cfg["concepts"].items():
    hits = census["concepts"].get(concept, {})
    alias = {}
    for canon, al in {**cfg.get("common_fields", {}), **(spec.get("aliases") or {})}.items():
        alias[canon] = canon
        for x in al: alias[snake(x)] = canon
    readable = {s: h for s, h in hits.items() if h["properties"]}
    fields = collections.defaultdict(lambda: {"providers": {}, "types": collections.Counter(), "spellings": collections.Counter()})
    for slug, h in readable.items():
        for name, typ in h["properties"].items():
            sn = snake(name)
            if not sn or sn in ENVELOPE or sn in spec["segments"]: continue
            canon = alias.get(sn, sn)
            f = fields[canon]
            f["providers"].setdefault(slug, []).append(name)
            f["spellings"][name] += 1
            if isinstance(typ, list): typ = next((t for t in typ if t != "null"), None)
            if typ in JSON_TYPES: f["types"][typ] += 1
    ops = collections.Counter()
    for h in hits.values():
        seen = set()
        for o in h["operations"]:
            m, shape = o.split()
            seen.add(f"{'UPDATE' if m in ('PUT', 'PATCH') else m} {shape}")
        ops.update(seen)

    denom = len(readable) or 1
    props = []
    for canon, f in fields.items():
        n = len(f["providers"])
        share = round(n / denom, 3)
        props.append({"name": canon, "tier": tier(share, n), "providers": n, "share": share,
                      "type": f["types"].most_common(1)[0][0] if f["types"] else None,
                      "spellings": [s for s, _ in f["spellings"].most_common(8)]})
    props.sort(key=lambda p: (-p["providers"], p["name"]))
    oplist = [{"operation": o, "providers": n, "share": round(n / (len(hits) or 1), 3),
               "tier": tier(n / (len(hits) or 1), n)} for o, n in ops.most_common()]
    profile["concepts"][concept] = {
        "segments_seen": dict(collections.Counter(s for h in hits.values() for s in h["segments"]).most_common()),
        "providers_exposing": len(hits), "providers_with_readable_schema": len(readable),
        "operations": oplist,
        "properties": [p for p in props if p["tier"] != "long-tail"],
        "long_tail_count": sum(1 for p in props if p["tier"] == "long-tail"),
        "long_tail_sample": [p["name"] for p in props if p["tier"] == "long-tail"][:40]}

    keep = [p for p in props if p["tier"] != "long-tail"]
    title = concept.replace("_", " ").title()
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema",
              "$id": f"{RAW}/schema/{concept}.json", "title": title,
              "description": f"The common {concept} in {cfg['name']}, distilled from {len(readable)} providers' "
                             f"own OpenAPI. Each property records the share of them that declare it.",
              "type": "object", "properties": {}, "required": ["id"] if any(p["name"] == "id" for p in keep) else [],
              "x-commons": {"context": CTX, "concept": concept, "providers": len(readable), "generated": TODAY}}
    for p in keep:
        s = {"x-commons-tier": p["tier"], "x-commons-share": p["share"], "x-commons-providers": p["providers"],
             "x-commons-spellings": p["spellings"]}
        if p["type"]: s = {"type": p["type"], **s}
        if p["name"].endswith("_at") and p["type"] in (None, "string"): s["format"] = "date-time"
        if p["name"] == "email" and p["type"] in (None, "string"): s["format"] = "email"
        schema["properties"][p["name"]] = s
    Path("schema").mkdir(exist_ok=True)
    json.dump(schema, open(f"schema/{concept}.json", "w"), indent=2)

    for slug, h in hits.items():
        adopters[slug][concept] = {"operations": h["operations"], "segments": h["segments"]}
        mapped = {p["name"]: fields[p["name"]]["providers"][slug] for p in keep if slug in fields[p["name"]]["providers"]}
        core = [p["name"] for p in keep if p["tier"] == "core"]
        crosswalks[slug][concept] = {
            "path_segment": h["segments"],
            "properties": {k: (v[0] if len(v) == 1 else v) for k, v in mapped.items()},
            "core_coverage": round(sum(1 for c in core if c in mapped) / (len(core) or 1), 3) if h["properties"] else None,
            "evidence": h["evidence"][:5]}

# OpenAPI: one collection + item path per concept, operations that clear the extended bar.
def pluralise(c): return {"activity": "activities", "company": "companies"}.get(c, c + "s")
VERB = {"GET collection": ("get", "list", "List"), "POST collection": ("post", "create", "Create"),
        "GET item": ("get", "get", "Get"), "UPDATE item": ("patch", "update", "Update"),
        "DELETE item": ("delete", "delete", "Delete")}
oas = {"openapi": "3.1.0",
       "info": {"title": f"{cfg['name']} (API Commons)", "version": TODAY,
                "description": f"The common {cfg['name']} interface, distilled from the harvested OpenAPI of "
                               f"{census['cohort_size']} providers in the APIs.io catalog. Not a product: no one "
                               "serves this API. It is the shape the market already shares, measured, so that "
                               "providers, agents and integrators can map to one vocabulary. See profile.yml.",
                "license": {"name": "CC BY-NC-SA 4.0", "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/"}},
       "paths": {}, "components": {"schemas": {}, "parameters": {}}}
for concept, c in profile["concepts"].items():
    plural = pluralise(concept)
    oas["components"]["schemas"][concept.title()] = {"$ref": f"./schema/{concept}.json"}
    oas["components"]["parameters"][f"{concept}_id"] = {"name": f"{concept}_id", "in": "path", "required": True,
                                                       "schema": {"type": "string"}}
    ref = {"$ref": f"#/components/schemas/{concept.title()}"}
    for o in c["operations"]:
        if o["tier"] == "long-tail" or o["operation"] not in VERB: continue
        m, verb, Verb = VERB[o["operation"]]
        item = o["operation"].endswith("item")
        path = f"/{plural}/{{{concept}_id}}" if item else f"/{plural}"
        op = {"operationId": f"{verb}{(plural if verb == 'list' else concept).title().replace('_', '')}",
              "summary": f"{Verb} {plural if verb == 'list' else 'a ' + concept}",
              "tags": [plural.title()], "x-commons-tier": o["tier"], "x-commons-share": o["share"],
              "responses": {"200": {"description": "OK", "content": {"application/json": {"schema":
                            {"type": "array", "items": ref} if verb == "list" else ref}}}}}
        if verb in ("create", "update"):
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref}}}
        if verb == "list":
            op["parameters"] = [{"name": "limit", "in": "query", "schema": {"type": "integer"}},
                                {"name": "cursor", "in": "query", "schema": {"type": "string"}}]
        if item:
            oas["paths"].setdefault(path, {})["parameters"] = [{"$ref": f"#/components/parameters/{concept}_id"}]
        oas["paths"].setdefault(path, {})[m] = op

Dumper = getattr(yaml, "CSafeDumper", yaml.SafeDumper)
dump = lambda o, p: yaml.dump(o, open(p, "w"), Dumper=Dumper, sort_keys=False, allow_unicode=True, width=110)
dump(profile, "profile.yml")
dump(oas, "openapi.yml")
Path("crosswalk").mkdir(exist_ok=True)
for slug, cw in crosswalks.items():
    dump({"provider": slug, "apis_io": f"https://apis.io/providers/{slug}/", "context": CTX,
          "generated": TODAY, "concepts": cw}, f"crosswalk/{slug}.yml")
dump({"context": CTX, "generated": TODAY, "adopters": [
      {"provider": s, "apis_io": f"https://apis.io/providers/{s}/", "crosswalk": f"crosswalk/{s}.yml",
       "concepts": sorted(c)} for s, c in sorted(adopters.items())]}, "adopters.yml")
for concept, c in profile["concepts"].items():
    core = [p["name"] for p in c["properties"] if p["tier"] == "core"]
    print(f"{concept:9} {c['providers_exposing']:3} exp / {c['providers_with_readable_schema']:3} readable  core: {', '.join(core)}", file=sys.stderr)
print(len(crosswalks), "crosswalks", file=sys.stderr)
