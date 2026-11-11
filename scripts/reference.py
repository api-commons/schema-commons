#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build a reference context: one whose shape a standard already owns.

A census context distils a vocabulary from what providers agree on. Where a standard has
already settled the shape (CAMARA for operator network APIs, STAC for imagery catalogs),
distilling it again would only re-derive the standard, badly. A reference context
publishes the standard's own objects as its schema (marked x-commons-source: standard,
linked to the pinned release) and measures, from each provider's harvested OpenAPI, which
of the standard's operations it implements and how much of each one's fields it carries.

concepts.yml carries a `reference:` block:
  reference:
    standard: camara-2025            # standards/<name>.yml, from extract-standard.py
    home: https://camaraproject.org
    publishers: [gsma, camara-project]   # catalog entries for the standard's own body: listed, not counted
    objects: [indicator]                 # optional: standard objects published in schema/ beyond the operations'
    mentions: '\bcamara\b'                  # optional: count providers whose specs name the standard at all
    object_threshold: 0.5                # optional: count a provider whose component schema carries this share
                                         # of a listed object's fields (a standard used as a format)
    match_objects: [indicator]           # optional: the objects distinctive enough to match on (default: objects)
    apis:                            # one entry per API in the standard
      - api: number-verification     # the slug a provider's path, server or title names it by
        release: https://github.com/camaraproject/NumberVerification/tree/r4.2
        operations:                  # METHOD path, as the standard publishes it
          - {op: POST /verify, request: NumberVerificationRequestBody, response: NumberVerificationMatchResponse}
        signature: [POST /verify]           # optional: operations only this API defines
        match: path                         # optional: the path alone identifies the API (OCI's /v2/<name>/...)
        path_contains: /v2/                 # optional: a path segment every operation of this API carries
        name: dcsa                          # optional: the token to match in path, server or title (default: api)
    min_coverage: 0.3                    # optional: an operation with standard fields must carry this share

Writes profile.yml, adopters.yml, crosswalk/<provider>.yml and schema/<object>.json.
Usage, from the context's directory: reference.py
"""
import json, re, shutil
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
ALL = Path("/Users/kinlane/Github/all")
cfg = yaml.safe_load(open("concepts.yml"))
ref = cfg["reference"]
std = yaml.safe_load(open(HUB / "standards" / f"{ref['standard']}.yml"))
OBJ = std["objects"]
cohort = json.load(open("census/cohort.json"))
# The standard body's own catalog listings carry its specs verbatim; they are not implementations.
PUBLISHERS = set(ref.get("publishers") or [])
# One company listed twice (a rename) counts once, under the canonical slug, as in census contexts.
DUP = {d: c for c, ds in (cfg.get("duplicates") or {}).items() for d in ds}


def norm(n):
    return re.sub(r"[^a-z0-9]", "", str(n).lower())


def load(p):
    text = p.read_text(errors="replace")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    try:
        return json.loads(text, strict=False) if text.lstrip().startswith("{") else yaml.safe_load(text)
    except Exception:
        return None


def resolve(doc, node, depth=0):
    while isinstance(node, dict) and "$ref" in node and depth < 20:
        cur = doc
        for part in node["$ref"].lstrip("#/").split("/"):
            cur = cur.get(part, {}) if isinstance(cur, dict) else {}
        node, depth = cur, depth + 1
    return node if isinstance(node, dict) else {}


def props(doc, s, depth=0):
    s = resolve(doc, s)
    if depth > 6:
        return set()
    out = set((s.get("properties") or {}).keys())
    for k in ("allOf", "oneOf", "anyOf"):
        for part in s.get(k) or []:
            out |= props(doc, part, depth + 1)
    if s.get("type") == "array" and s.get("items"):
        out |= props(doc, s["items"], depth + 1)
    return out


def body_props(doc, op):
    req, res = set(), set()
    rb = resolve(doc, op.get("requestBody") or {})
    for media in (rb.get("content") or {}).values():
        req |= props(doc, media.get("schema") or {})
    for code, r in (op.get("responses") or {}).items():
        if str(code).startswith("2"):
            for media in (resolve(doc, r).get("content") or {}).values():
                res |= props(doc, media.get("schema") or {})
    return req, res


def names_api(api, doc, path, spec):
    """Does this operation belong to the standard API named `api`? CAMARA puts the API name in
    the server base path, so a bare /verify is only matched when the server, path, title or
    file names it."""
    hay = " ".join([path, spec.name, str((doc.get("info") or {}).get("title", ""))] +
                   [str(s.get("url", "")) for s in doc.get("servers") or [] if isinstance(s, dict)])
    if "-" in api:  # a multi-word name is distinctive however it is cased (NumberVerification)
        return norm(api) in norm(hay)
    # a single word must stand alone: "stac" is not in "sift-stack"
    return re.search(rf"(^|[^a-z0-9]){re.escape(api)}([^a-z0-9]|$)", hay.lower()) is not None


def canon(path):
    """A path template with every parameter as {} -- <name>, {repository} and {name} are one slot."""
    return re.sub(r"[{<][^}>]+[}>]", "{}", path).rstrip("/")


def std_fields(obj):
    return [f for f in OBJ.get(obj, [])]


shutil.rmtree("crosswalk", ignore_errors=True); Path("crosswalk").mkdir()
shutil.rmtree("schema", ignore_errors=True); Path("schema").mkdir()
# How many providers name the standard at all, anywhere in a harvested spec: the gap between
# mentioning a standard and implementing it is part of the finding.
mentioned = []
if ref.get("mentions"):
    pat = re.compile(ref["mentions"], re.I)
    for entry in cohort:
        for rel in entry["specs"]:
            spec = ALL / entry["slug"] / rel
            if spec.exists() and pat.search(spec.read_text(errors="replace")):
                mentioned.append(entry["slug"]); break
adopters, per_api = [], {a["api"]: [] for a in ref["apis"]}
if ref.get("object_threshold"):
    per_api["objects"] = []
for entry in cohort:
    slug, found = entry["slug"], {}
    for rel in entry["specs"]:
        spec = ALL / slug / rel
        doc = load(spec) if spec.exists() else None
        if not isinstance(doc, dict):
            continue
        for path, item in (doc.get("paths") or {}).items():
            if not isinstance(item, dict):
                continue
            for a in ref["apis"]:
                for o in a["operations"]:
                    method, spath = o["op"].split(" ", 1)
                    op = item.get(method.lower())
                    if not isinstance(op, dict) or not canon(path).endswith(canon(spath)) \
                            or (a.get("match") != "path" and not names_api(a.get("name", a["api"]), doc, path, spec)) \
                            or (a.get("path_contains") and a["path_contains"] not in path):
                        continue
                    req, res = body_props(doc, op)
                    have = {norm(x): x for x in req | res}
                    want = std_fields(o.get("request")) + std_fields(o.get("response"))
                    cw = {f: have[norm(f)] for f in want if norm(f) in have}
                    # Matched on path alone, an operation that carries standard fields must carry enough
                    # of them to count; one whose path or server names the standard counts as it is.
                    if a.get("match") == "path" and want and len(cw) / len(want) < (ref.get("min_coverage") or 0):
                        continue
                    key = (a["api"], o["op"])
                    if key not in found or len(cw) > len(found[key]["crosswalk"]):
                        found[key] = {"api": a["api"], "operation": o["op"], "evidence": f"{rel}#{method} {path}",
                                      "fields": len(want), "crosswalk": cw,
                                      "coverage": round(len(cw) / len(want), 2) if want else None}
    # Object match: a standard used as a format (STIX objects in an export, an ingest config)
    # shows in a provider's component schemas rather than its paths. Any schema carrying at
    # least `object_threshold` of a listed object's fields counts, best schema per object.
    if ref.get("object_threshold"):
        for rel in entry["specs"]:
            spec = ALL / slug / rel
            doc = load(spec) if spec.exists() else None
            if not isinstance(doc, dict):
                continue
            comps = ((doc.get("components") or {}).get("schemas")) or doc.get("definitions") or {}
            for sname, sch in comps.items():
                have = {norm(x): x for x in props(doc, sch)}
                for obj in ref.get("match_objects") or ref.get("objects") or []:
                    want = OBJ.get(obj, [])
                    cw = {f: have[norm(f)] for f in want if norm(f) in have}
                    cov_ = round(len(cw) / len(want), 2) if want else 0
                    key = ("objects", obj)
                    if cov_ >= ref["object_threshold"] and (key not in found or cov_ > found[key]["coverage"]):
                        found[key] = {"api": "objects", "operation": obj, "evidence": f"{rel}#/components/schemas/{sname}",
                                      "fields": len(want), "crosswalk": cw, "coverage": cov_}
    # An API's `signature` operations are the ones only it defines (STAC's /search; /collections
    # alone is plain OGC API Features). Without one, the provider does not implement that API.
    for a in ref["apis"]:
        sig = set(a.get("signature") or [])
        if sig and not any(k[0] == a["api"] and k[1] in sig for k in found):
            found = {k: v for k, v in found.items() if k[0] != a["api"]}
    if found and slug in DUP:
        continue  # merged: the canonical listing carries this company
    if found:
        ops = sorted(found.values(), key=lambda x: (x["api"], x["operation"]))
        yaml.safe_dump({"provider": slug, "standard": ref["standard"], "operations": ops},
                       open(f"crosswalk/{slug}.yml", "w"), sort_keys=False, width=120)
        apis = sorted({o["api"] for o in ops})
        role = "publisher" if slug in PUBLISHERS else "implementer"
        adopters.append({"provider": slug, "role": role, "apis": apis,
                         "url": f"https://apis.io/providers/{slug}/"})
        if role == "implementer":
            for a in apis:
                per_api[a].append(slug)

# The schema is the standard's own objects, linked to the release they came from: the ones
# operations carry, plus any the reference block lists under `objects` (STIX objects that a
# TAXII operation returns inside its envelope).
for obj in ref.get("objects") or []:
    if obj in OBJ:
        json.dump({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": obj, "type": "object",
                   "x-commons-source": "standard", "x-commons-standard": ref["standard"],
                   "x-commons-release": ref.get("release") or ref["home"],
                   "properties": {f: {} for f in OBJ[obj]}}, open(f"schema/{obj}.json", "w"), indent=2)
for a in ref["apis"]:
    for o in a["operations"]:
        for obj in (o.get("request"), o.get("response")):
            if obj and obj in OBJ:
                json.dump({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": obj,
                           "type": "object", "x-commons-source": "standard",
                           "x-commons-standard": ref["standard"], "x-commons-release": a["release"],
                           "properties": {f: {} for f in OBJ[obj]}},
                          open(f"schema/{obj}.json", "w"), indent=2)

profile = {"context": cfg["context"], "kind": "reference", "standard": ref["standard"],
           "cohort": {"tags": cfg["tags"], "providers_with_harvested_openapi": len(cohort)},
           "implementers": sum(1 for a in adopters if a["role"] == "implementer"),
           "publishers": sorted(a["provider"] for a in adopters if a["role"] == "publisher"),
           "mentioned_by": len(mentioned), "mentioned_by_providers": sorted(mentioned),
           "apis": {a["api"]: {"release": a["release"], "providers": len(per_api[a["api"]]),
                               "operations": [o["op"] for o in a["operations"]]} for a in ref["apis"]}}
yaml.safe_dump(profile, open("profile.yml", "w"), sort_keys=False, width=120)
yaml.safe_dump({"adopters": adopters}, open("adopters.yml", "w"), sort_keys=False, width=120)
print(f"{profile['implementers']} of {len(cohort)} providers implement {ref['standard']}; "
      f"{len(mentioned)} name it in a spec "
      f"(publishers listed, not counted: {', '.join(profile['publishers'])})")
for a, ps in per_api.items():
    print(f"  {a:30} {len(ps):3}  {', '.join(ps[:8])}{' ...' if len(ps) > 8 else ''}")

# README: generated from concepts.yml and the measurement, like every context's.
cov = {}
for f in Path("crosswalk").glob("*.yml"):
    d = yaml.safe_load(open(f))
    for o in d["operations"]:
        cov.setdefault(d["provider"], {}).setdefault(o["api"], []).append(o["coverage"])
L = [f"# {cfg['name']}", "", " ".join(cfg["intro"].split()), "",
     f"**A reference context.** The shape belongs to [{ref['standard']}]({ref['home']}) "
     f"({ref.get('license', 'see the standard')}). This repository does not restate or rename it: "
     "`schema/` holds the standard's own objects, each linked to the release it was read from, and "
     "`crosswalk/` measures, from each provider's harvested OpenAPI, which operations it implements "
     "and what share of the standard's request and response fields it carries.", "",
     f"Measured across {len(cohort)} providers tagged {', '.join(map(str, cfg['tags']))} in "
     f"[APIs.io](https://apis.io): **{profile['implementers']} implement the standard**"
     + (f"; {profile['mentioned_by']} name it somewhere in a spec." if ref.get("mentions") else "."), "",
     "## The standard's APIs", "", "| API | Release | Implementers | Operations |", "| --- | --- | ---: | --- |"]
for a in ref["apis"]:
    L.append(f"| {a['api']} | [{a['release'].rsplit('/', 1)[-1]}]({a['release']}) | "
             f"{len(per_api[a['api']])} | {', '.join('`' + o['op'] + '`' for o in a['operations'])} |")
L += ["", "## Implementers", "",
      "Coverage is the best-matching operation's share of the standard's fields, per API.", "",
      "| Provider | APIs (field coverage) |", "| --- | --- |"]
for ad in sorted(adopters, key=lambda x: (x["role"], x["provider"])):
    if ad["role"] != "implementer":
        continue
    cells = ", ".join(f"{a} {max(x for x in v if x is not None):.0%}" if any(x is not None for x in v)
                      else f"{a} ({len(v)} operations)" for a, v in sorted(cov[ad["provider"]].items()))
    L.append(f"| [{ad['provider']}]({ad['url']}) | {cells} |")
if profile["publishers"]:
    L += ["", "The standard's own publishing bodies are listed in the catalog too ("
          + ", ".join(f"[{p}](https://apis.io/providers/{p}/)" for p in profile["publishers"])
          + "); they carry the specifications verbatim and are not counted as implementers."]
for title, key in (("Findings", "findings"), ("Decisions", "decisions")):
    if cfg.get(key):
        L += ["", f"## {title}", ""] + [f"- {' '.join(x.split())}" for x in cfg[key]]
L += ["", "## Licence", "",
      "Measurements (profile, crosswalks, adopters) are CC BY-NC-SA 4.0; code is Apache 2.0. The "
      f"standard's objects in `schema/` remain under the standard's own licence ({ref.get('license', 'see the standard')}).", ""]
Path("README.md").write_text("\n".join(L))
