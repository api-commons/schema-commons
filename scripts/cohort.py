#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build the cohort for a bounded context: providers tagged with one of the context's
tags whose repository holds at least one HARVESTED OpenAPI (openapi/_original/, recorded
as method: harvested in provenance.yml). Generated or derived contracts never count —
the commons distills what providers publish, not what we wrote about them."""
import argparse, json, re, sys
from pathlib import Path
import yaml
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

ALL = Path("/Users/kinlane/Github/all")
ap = argparse.ArgumentParser()
ap.add_argument("--tags", nargs="+", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
want = {t.lower() for t in a.tags}
TAG = re.compile(r"^tags:[ \t]*\n((?:[ \t]*- .*\n)+)", re.M)

cohort = []
for apis in ALL.glob("*/apis.yml"):
    slug = apis.parent.name
    try:
        m = TAG.search(apis.read_text(errors="ignore"))
    except OSError:
        continue
    if not m or not want & {l.strip()[2:].strip().strip("'\"").lower() for l in m.group(1).splitlines()}:
        continue
    orig = apis.parent / "openapi" / "_original"
    prov = apis.parent / "provenance.yml"
    if not orig.is_dir() or not prov.exists():
        continue
    try:
        arts = (yaml.load(prov.read_text(), Loader=Loader) or {}).get("artifacts") or {}
    except yaml.YAMLError:
        continue
    specs = sorted(k for k, v in arts.items()
                   if k.startswith("openapi/_original/") and (v or {}).get("method") == "harvested"
                   and re.search(r"\.(ya?ml|json)$", k) and (apis.parent / k).exists())
    if specs:
        cohort.append({"slug": slug, "specs": specs})
json.dump(sorted(cohort, key=lambda c: c["slug"]), open(a.out, "w"), indent=1)
print(len(cohort), "providers,", sum(len(c["specs"]) for c in cohort), "harvested specs", file=sys.stderr)
