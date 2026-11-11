#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure a bounded context across its cohort's harvested OpenAPI.

For every concept in concepts.yml it finds the collection each provider exposes (by the
path segment the provider actually uses), the operations on it, and the properties of the
resource schema behind it. Every count is a count of PROVIDERS, never of specs, so one
company publishing forty files weighs the same as one publishing one.

It also measures the naming conventions the cohort uses (path, property and parameter
case, identifier and timestamp naming, pagination parameters), which is the evidence the
common naming ruleset cites.

Writes census.json: per concept, per property, the providers that declare it and the
exact name and path each one uses -- the crosswalk is the raw material, the profile is
built from it."""
import argparse, collections, json, re, sys
from pathlib import Path
import yaml
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

ALL = Path("/Users/kinlane/Github/all")
HERE = Path.cwd()  # run from the context repo
ap = argparse.ArgumentParser()
ap.add_argument("--cohort", required=True)
ap.add_argument("--concepts", default="concepts.yml")
ap.add_argument("--out", default="census/census.json")
a = ap.parse_args()

CONCEPTS = yaml.safe_load(open(a.concepts))["concepts"]
SEG2CONCEPT = {s: c for c, d in CONCEPTS.items() for s in d["segments"]}
PARAM = re.compile(r"^\{.*\}$")
METHODS = ("get", "post", "put", "patch", "delete")


def snake(name):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def case_of(name):
    if re.fullmatch(r"[a-z][a-z0-9]*", name): return "lower"
    if re.fullmatch(r"[a-z][a-z0-9]*(_[a-z0-9]+)+", name): return "snake_case"
    if re.fullmatch(r"[a-z][a-z0-9]*([A-Z][a-z0-9]*)+", name): return "camelCase"
    if re.fullmatch(r"[A-Z][a-zA-Z0-9]*", name): return "PascalCase"
    if re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)+", name): return "kebab-case"
    return "other"


def load(p):
    try:
        t = p.read_text(errors="ignore")
        return json.loads(t) if p.suffix == ".json" else yaml.load(t, Loader=Loader)
    except Exception:
        return None


def resolve(doc, node, depth=0):
    while isinstance(node, dict) and "$ref" in node and depth < 12:
        ref = node["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"): return {}
        cur = doc
        for part in ref[2:].split("/"):
            cur = cur.get(part.replace("~1", "/").replace("~0", "~"), {}) if isinstance(cur, dict) else {}
        node, depth = cur, depth + 1
    return node if isinstance(node, dict) else {}


def props_of(doc, schema, depth=0):
    """Top-level properties of a resource schema, unwrapping arrays, allOf and the common
    envelopes (data / results / items / a lone wrapper object)."""
    s = resolve(doc, schema)
    if depth > 6 or not s: return {}
    if s.get("type") == "array" or "items" in s and "properties" not in s:
        return props_of(doc, s.get("items", {}), depth + 1)
    out = {}
    for sub in s.get("allOf", []) or []:
        out.update(props_of(doc, sub, depth + 1))
    for key in ("oneOf", "anyOf"):
        if not out and s.get(key):
            out.update(props_of(doc, s[key][0], depth + 1))
    p = s.get("properties") or {}
    if isinstance(p, dict):
        for env in ("data", "results", "items", "records", "result"):
            if env in p and len(p) <= 6:
                inner = props_of(doc, p[env], depth + 1)
                if inner: return inner
        if len(p) == 1:
            inner = props_of(doc, next(iter(p.values())), depth + 1)
            if len(inner) > 2: return inner
        for k, v in p.items():
            v = resolve(doc, v)
            out[k] = v.get("type") or ("object" if "properties" in v else "array" if "items" in v else None)
    return out


def body_schema(doc, op, responses=True):
    if not isinstance(op, dict): return None
    if responses:
        r = (op.get("responses") or {})
        r = r.get("200") or r.get(200) or r.get("201") or r.get(201) or {}
        r = resolve(doc, r)
        if "schema" in r: return r["schema"]                      # swagger 2
        c = r.get("content") or {}
    else:
        rb = resolve(doc, op.get("requestBody") or {})
        if not rb:
            for prm in op.get("parameters") or []:
                prm = resolve(doc, prm)
                if prm.get("in") == "body": return prm.get("schema")
            return None
        c = rb.get("content") or {}
    for mt, m in c.items():
        if "json" in mt and isinstance(m, dict) and m.get("schema"): return m["schema"]
    return None


cohort = json.load(open(a.cohort))
concept_hits = {c: {} for c in CONCEPTS}           # concept -> slug -> {...}
naming = collections.defaultdict(lambda: collections.defaultdict(set))  # dimension -> value -> slugs

for prov in cohort:
    slug = prov["slug"]
    for rel in prov["specs"]:
        doc = load(ALL / slug / rel)
        if not isinstance(doc, dict) or not isinstance(doc.get("paths"), dict): continue
        for path, item in doc["paths"].items():
            if not isinstance(item, dict) or not isinstance(path, str): continue
            segs = [s for s in path.split("/") if s]
            for s in segs:
                if PARAM.match(s):
                    naming["path_param"][case_of(s[1:-1])].add(slug)
                elif not re.fullmatch(r"v\d+.*|api|\$.*", s, re.I):
                    naming["path_segment"][case_of(s)].add(slug)
            lits = [(i, s.lower()) for i, s in enumerate(segs) if not PARAM.match(s)]
            hit = None
            for i, s in reversed(lits):
                if s in SEG2CONCEPT:
                    hit = (i, s); break
            for m in METHODS:
                op = item.get(m)
                if not isinstance(op, dict): continue
                for prm in (op.get("parameters") or []) + (item.get("parameters") or []):
                    prm = resolve(doc, prm)
                    n = prm.get("name")
                    if prm.get("in") == "query" and isinstance(n, str):
                        naming["query_param"][case_of(n)].add(slug)
                        if snake(n) in ("limit", "offset", "page", "per_page", "page_size", "cursor",
                                        "after", "before", "start", "page_token", "next", "count",
                                        "size", "skip", "top", "max_results", "starting_after"):
                            naming["pagination_param"][snake(n)].add(slug)
                if not hit: continue
                i, seg = hit
                concept = SEG2CONCEPT[seg]
                rest = segs[i + 1:]
                if len(rest) > 1 or (rest and not PARAM.match(rest[0])): continue
                shape = "item" if rest else "collection"
                h = concept_hits[concept].setdefault(slug, {"segments": set(), "operations": set(),
                                                            "properties": {}, "evidence": set()})
                h["segments"].add(seg)
                h["operations"].add(f"{m.upper()} {shape}")
                h["evidence"].add(f"{rel}#{m.upper()} {path}")
                for sch in (body_schema(doc, op), body_schema(doc, op, responses=False)):
                    if sch is None: continue
                    for name, typ in props_of(doc, sch).items():
                        if not isinstance(name, str): continue
                        h["properties"].setdefault(name, typ)
                        naming["property"][case_of(name)].add(slug)

out = {"cohort_size": len(cohort), "concepts": {}, "naming": {}}
for c, provs in concept_hits.items():
    out["concepts"][c] = {slug: {"segments": sorted(h["segments"]), "operations": sorted(h["operations"]),
                                 "properties": h["properties"], "evidence": sorted(h["evidence"])[:12]}
                          for slug, h in sorted(provs.items())}
for dim, vals in naming.items():
    out["naming"][dim] = {v: sorted(s) for v, s in sorted(vals.items(), key=lambda kv: -len(kv[1]))}
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
json.dump(out, open(a.out, "w"), indent=1)
for c, provs in out["concepts"].items():
    print(f"{c:12} {len(provs):4} providers  {sum(1 for p in provs.values() if p['properties']):4} with a readable schema", file=sys.stderr)
