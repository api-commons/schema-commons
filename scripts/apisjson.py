#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Write a context repo's APIs.json index (apis.yml) from concepts.yml and profile.yml.
Run from the context repo after build.py."""
from datetime import date
import yaml

cfg = yaml.safe_load(open("concepts.yml"))
profile = yaml.safe_load(open("profile.yml"))
ctx, name = cfg["context"], cfg["name"]
R = f"https://raw.githubusercontent.com/api-commons/{ctx}/main"
try:
    created = yaml.safe_load(open("apis.yml"))["created"]
except (OSError, KeyError, TypeError):
    created = date.today().isoformat()
n = profile["cohort"]["providers_with_harvested_openapi"]
doc = {"aid": f"common-{ctx}", "name": name, "type": "Common",
       "description": f"The common {name} vocabulary, distilled from the harvested OpenAPI of {n} providers in "
                      "APIs.io: shared operations, JSON Schema per concept with measured adoption, and a crosswalk "
                      "from the common names to each provider's own.",
       "image": "https://kinlane-productions.s3.amazonaws.com/apis-json/apis-json-logo.jpg",
       "tags": ["Application Programming Interface", "API", *cfg["tags"][:4], "Common Schema"],
       "created": str(created), "modified": date.today().isoformat(), "url": f"{R}/apis.yml",
       "specificationVersion": "0.20",
       "apis": [{"aid": f"common-{ctx}:{ctx}", "name": f"Common {name} Interface",
                 "description": f"The {name} interface the market already shares, measured.",
                 "humanURL": f"https://github.com/api-commons/{ctx}", "tags": cfg["tags"][:2],
                 "properties": [{"type": "OpenAPI", "url": f"{R}/openapi.yml"},
                                {"type": "Profile", "url": f"{R}/profile.yml"},
                                {"type": "Adopters", "url": f"{R}/adopters.yml"},
                                {"type": "Rules", "url": "https://raw.githubusercontent.com/api-commons/schema-commons/main/ruleset/schema-commons-naming.yaml"}]
                               + [{"type": "JSONSchema", "name": c, "url": f"{R}/schema/{c}.json"} for c in profile["concepts"]]}],
       "common": [{"type": "License", "url": f"{R}/LICENSE"}],
       "maintainers": [{"FN": "Kin Lane", "email": "kin@apievangelist.com"}]}
yaml.safe_dump(doc, open("apis.yml", "w"), sort_keys=False, width=110)
