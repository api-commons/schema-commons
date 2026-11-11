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
        objects[Path(f).stem.split("-")[-1]] = [k for k in (d.get("properties") or {}) if not k.startswith("@")]
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
elif fmt == "reso":
    text = Path(files[0]).read_text()
    for m in re.finditer(r'<EntityType Name="([^"]+)"(.*?)</EntityType>', text, re.S):
        objects[m.group(1)] = re.findall(r'<Property Name="([^"]+)"', m.group(2))

out = {"standard": name, "source": url, "format": fmt,
       "note": "Field names extracted from the standard's own published definition by "
               "scripts/extract-standard.py; nothing here comes from a provider's spec.",
       "objects": {k: v for k, v in objects.items() if v}}
p = Path(__file__).resolve().parent.parent / "standards" / f"{name}.yml"
yaml.safe_dump(out, open(p, "w"), sort_keys=False, width=120)
print(name, {k: len(v) for k, v in out["objects"].items()} if len(out["objects"]) < 15 else f"{len(out['objects'])} objects")
