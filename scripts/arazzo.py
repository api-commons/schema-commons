#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Write a context's Arazzo 1.0 document from the `workflows:` declared in concepts.yml.

These are reference compositions, not measurements: there is no provider-authored Arazzo
in the catalog to measure. So every step must be an operation the census put in the core
or extended tier of the context's common OpenAPI -- a workflow may only be built from what
the market already shares -- and the build refuses a step whose operation does not exist.

  workflows:
    - id: create-contact-with-deal
      summary: Create a contact, then open a deal for them
      steps:
        - {op: createContact, id: contact}
        - {op: createDeal, id: deal, link: {contact_id: "$steps.contact.outputs.id"}}
"""
import re, sys
import yaml

cfg = yaml.safe_load(open("concepts.yml"))
oas = yaml.safe_load(open("openapi.yml"))
ops = {o["operationId"]: (path, m, o) for path, item in oas["paths"].items()
       for m, o in item.items() if isinstance(o, dict) and "operationId" in o}
wfs = cfg.get("workflows") or []
if not wfs:
    sys.exit(0)
doc = {"arazzo": "1.0.1",
       "info": {"title": f"{cfg['name']} workflows (API Commons)", "version": oas["info"]["version"],
                "summary": f"Reference workflows over the common {cfg['name']} operations.",
                "description": "Reference compositions of the operations this context's providers share. Not measured: "
                               "every step is a core- or extended-tier operation of the common OpenAPI, so the workflow "
                               "runs against any provider that implements those operations (see crosswalk/)."},
       "sourceDescriptions": [{"name": cfg["context"], "url": "./openapi.yml", "type": "openapi"}],
       "workflows": []}
bad = []
for w in wfs:
    steps = []
    for st in w["steps"]:
        if st["op"] not in ops:
            bad.append(f"{w['id']}: {st['op']}"); continue
        path, method, op = ops[st["op"]]
        step = {"stepId": st["id"], "operationId": st["op"],
                "description": f"{op.get('summary', st['op'])} -- a {op.get('x-commons-tier')}-tier operation "
                               f"({round(op.get('x-commons-share', 0) * 100)}% of providers).",
                "successCriteria": [{"condition": "$statusCode == 200"}],
                "outputs": {"id": "$response.body#/id"}}
        params = [{"name": p.split("}")[0].split("{")[1], "in": "path", "value": v}
                  for p, v in (st.get("path") or {}).items()]
        if params:
            step["parameters"] = params
        if st.get("link"):
            step["requestBody"] = {"contentType": "application/json", "payload": st["link"]}
        steps.append(step)
    used = sorted(set(re.findall(r"\$inputs\.(\w+)", yaml.safe_dump(w))))
    wf = {"workflowId": w["id"], "summary": w["summary"], "description": w.get("description") or w["summary"] + "."}
    if used:
        wf["inputs"] = {"type": "object", "required": used, "properties": {u: {"type": "string"} for u in used}}
    doc["workflows"].append({**wf, "steps": steps,
                             "x-commons-tiers": sorted({ops[s["op"]][2].get("x-commons-tier") for s in w["steps"] if s["op"] in ops})})
if bad:
    sys.exit("steps reference operations not in the common OpenAPI: " + ", ".join(bad))
yaml.safe_dump(doc, open("arazzo.yml", "w"), sort_keys=False, width=110)
print(f"{len(doc['workflows'])} workflows")
