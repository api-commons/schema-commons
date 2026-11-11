#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Extract a standard's own field names per object into standards/<name>.yml, from the
standard's published source (not from any provider's spec). One reader per source format:

  ocpi  AsciiDoc module specs (ocpi/ocpi on GitHub): "Object" sections and their property tables
  otlp  Protocol Buffers (open-telemetry/opentelemetry-proto): message fields, JSON-mapped
  cap   XML Schema (OASIS CAP 1.2): alert and info elements
  reso  OData EDMX (RESO Data Dictionary 2.0): entity type properties
  jsonschema  JSON Schema files, one object per file (DCAT-US 1.1)
  openapi  OpenAPI component schemas, allOf and $refs followed (CAMARA)
  oci   OCI Distribution spec.md endpoint table: the standard's operations
  schemaorg  schema.org JSON-LD release: properties of each type in SCHEMAORG_TYPES, inherited ones included

Usage: extract-standard.py <format> <out-name> <source-url> <file> [<file> ...]"""
import re, sys
from pathlib import Path
import yaml

fmt, name, url, files = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
objects = {}

if fmt == "ocpi":
    for f in files:
        text = Path(f).read_text()
        for m in re.finditer(r"^=+ +_?([A-Za-z]+)_? +Object\s*$(.*?)(?=^=+ +\S|\Z)", text, re.M | re.S):
            fields = re.findall(r"^\|\s*([a-z][a-z0-9_]*)\s*\|", m.group(2), re.M)
            if fields:
                objects.setdefault(m.group(1), [])
                objects[m.group(1)] += [x for x in fields if x not in objects[m.group(1)]]
elif fmt == "otlp":
    for f in files:
        text = Path(f).read_text()
        for m in re.finditer(r"^message (\w+) \{(.*?)^\}", text, re.M | re.S):
            body = re.sub(r"^\s+(enum|message) \w+ \{.*?^\s+\}", "", m.group(2), flags=re.M | re.S)
            fields = re.findall(r"^\s+(?:repeated\s+|optional\s+)?[\w.]+\s+(\w+)\s*=\s*\d+", body, re.M)
            if fields:
                objects[m.group(1)] = fields
elif fmt == "cap":
    import xml.etree.ElementTree as ET
    XS = "{http://www.w3.org/2001/XMLSchema}"
    def children(el):
        seq = el.find(f"{XS}complexType/{XS}sequence")
        return [] if seq is None else seq.findall(f"{XS}element")
    def walk(el):
        kids = children(el)
        if kids:
            objects[el.get("name")] = [k.get("name") for k in kids]
            for k in kids:
                walk(k)
    walk(ET.parse(files[0]).getroot().find(f"{XS}element"))
elif fmt == "jsonschema":
    import json
    for f in files:
        d = json.load(open(f))
        top = [k for k in (d.get("properties") or {}) if not k.startswith("@")]
        # STIX: properties live in a top-level allOf -- inline parts, and relative-file $refs
        # (../common/core.json) read from beside the file.
        for part in d.get("allOf") or []:
            src = part
            if str(part.get("$ref", "")).endswith(".json"):
                ref = (Path(f).parent / part["$ref"]).resolve()
                src = json.load(open(ref)) if ref.exists() else {}
            top += [k for k in (src.get("properties") or {}) if k not in top and not k.startswith("@")]
        if top:
            objects[Path(f).stem] = top
        # Each definition is an object too (STAC items, OCDS awards), with allOf/oneOf/anyOf
        # parts and local #/definitions or #/$defs refs followed.
        defs = d.get("definitions") or d.get("$defs") or {}
        def dprops(n, seen=()):
            if "$ref" in n and n["$ref"].startswith(("#/definitions/", "#/$defs/")):
                r = n["$ref"].split("/")[-1]
                return [] if r in seen else dprops(defs.get(r, {}), seen + (r,))
            out = [k for k in (n.get("properties") or {})]
            for part in (n.get("allOf") or []) + (n.get("oneOf") or []) + (n.get("anyOf") or []):
                out += [k for k in dprops(part, seen) if k not in out]
            return out
        for k, n in defs.items():
            if dprops(n):
                objects[f"{Path(f).stem}.{k}"] = dprops(n)
elif fmt == "openapi":
    # A standard published as OpenAPI (CAMARA): each component schema's properties, with
    # allOf parts and local $refs followed, so a request body lists what a caller sends.
    for f in files:
        d = yaml.safe_load(open(f))
        schemas = (d.get("components") or {}).get("schemas") or {}
        def props(s, seen=()):
            if "$ref" in s:
                ref = s["$ref"].split("/")[-1]
                return [] if ref in seen else props(schemas.get(ref, {}), seen + (ref,))
            out = list((s.get("properties") or {}))
            for part in s.get("allOf") or []:
                out += [p for p in props(part, seen) if p not in out]
            return out
        for k, s in schemas.items():
            if k not in objects and props(s):
                objects[k] = props(s)
elif fmt == "oci":
    # OCI Distribution: the endpoint table in spec.md (end-1 ... end-13). The standard is its
    # operations; request and response bodies are image-spec documents, not objects here.
    ops = []
    for f in files:
        for m in re.finditer(r"^\|\s*(end-\w+)\s*\|\s*([^|]+)\|\s*`([^`]+)`", Path(f).read_text(), re.M):
            for method in re.findall(r"`(\w+)`", m.group(2)):
                op = f"{method} {m.group(3).split('?')[0]}"
                if op not in ops:
                    ops.append(op)
    objects["endpoints"] = ops
elif fmt == "schemaorg":
    # schema.org JSON-LD release: for each type named in SCHEMAORG_TYPES, every property whose
    # domainIncludes is the type or one of its supertypes (JobPosting inherits Thing's name, url).
    import json, os
    graph = json.load(open(files[0]))["@graph"]
    sid = lambda x: x.split(":")[-1] if isinstance(x, str) else x.get("@id", "").split(":")[-1]
    as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])
    parents = {sid(n["@id"]): [sid(p) for p in as_list(n.get("rdfs:subClassOf"))]
               for n in graph if n.get("@type") == "rdfs:Class"}
    domains = {}
    for n in graph:
        if n.get("@type") == "rdf:Property" and "schema:supersededBy" not in n:
            for d in as_list(n.get("schema:domainIncludes")):
                domains.setdefault(sid(d), []).append(sid(n["@id"]))
    def lineage(t, seen=()):
        out = [t]
        for p in parents.get(t, []):
            if p not in seen:
                out += [x for x in lineage(p, seen + (t,)) if x not in out]
        return out
    for t in os.environ["SCHEMAORG_TYPES"].split(","):
        objects[t] = [p for a in lineage(t) for p in sorted(domains.get(a, []))]
elif fmt == "reso":
    text = Path(files[0]).read_text()
    for m in re.finditer(r'<EntityType Name="([^"]+)"(.*?)</EntityType>', text, re.S):
        objects[m.group(1)] = re.findall(r'<Property Name="([^"]+)"', m.group(2))

p = Path(__file__).resolve().parent.parent / "standards" / f"{name}.yml"
# MERGE=1 adds this run's objects to an existing standard file: one standard published in two
# formats (STAC: an OpenAPI API spec and JSON Schema object specs) is still one standard.
import os
if os.environ.get("MERGE") and p.exists():
    prev = yaml.safe_load(open(p))
    objects = {**prev["objects"], **objects}
    url, fmt = f"{prev['source']} + {url}", f"{prev['format']}+{fmt}"
out = {"standard": name, "source": url, "format": fmt,
       "note": "Field names extracted from the standard's own published definition by "
               "scripts/extract-standard.py; nothing here comes from a provider's spec.",
       "objects": {k: v for k, v in objects.items() if v}}
yaml.safe_dump(out, open(p, "w"), sort_keys=False, width=120)
print(name, {k: len(v) for k, v in out["objects"].items()} if len(out["objects"]) < 15 else f"{len(out['objects'])} objects")
