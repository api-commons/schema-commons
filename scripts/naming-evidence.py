#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure the naming conventions the naming ruleset cites, across every built context.

Reads each context's census/census.json (listed in contexts.yml) and counts PROVIDERS per
convention, union across contexts, with catalog duplicates folded into one company.
Writes evidence/naming.yml. The numbers in the ruleset's rule descriptions are copied from
this file; re-run it whenever a context is added or rebuilt, then update the ruleset."""
import collections, json, re
from datetime import date
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
ctxs = [c for c in yaml.safe_load(open(HUB / "contexts.yml"))["contexts"] if c["status"] != "planned"]


def snake(n):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", n))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


m = collections.defaultdict(lambda: collections.defaultdict(set))
cohort = set()
for c in ctxs:
    repo = HUB.parent / c["context"]
    cfg = yaml.safe_load(open(repo / "concepts.yml"))
    dup = {d: k for k, ds in (cfg.get("duplicates") or {}).items() for d in ds}
    # A shared specification is one voice in naming too (see build.py).
    dup.update({m: k for k, ms in (cfg.get("shared_specs") or {}).items() for m in ms})
    census = json.load(open(repo / "census" / "census.json"))
    cohort |= {dup.get(x["slug"], x["slug"]) for x in json.load(open(repo / "census" / "cohort.json"))}
    for dim, vals in census["naming"].items():
        for v, slugs in vals.items():
            m[dim][v] |= {dup.get(s, s) for s in slugs}
    for concept, provs in census["concepts"].items():
        for s, h in provs.items():
            s = dup.get(s, s)
            for seg in h["segments"]:
                m["collection_noun"]["plural" if seg.endswith("s") else "singular"].add(s)
            for n in h["properties"]:
                sn = snake(n)
                if re.match(r"^(created|updated|modified)", sn) or re.match(r"^(add|update|create|modify)_?time$", sn):
                    form = "_at" if sn.endswith("_at") else "_date/_time/on" if re.search(r"(date|time|on)$", sn) else "bare"
                    m["timestamp"][form].add(s)
                if n not in ("id", "ID") and re.search(r"(Id|ID|_id)$", n):
                    m["foreign_key"]["_id" if n.endswith("_id") else "Id"].add(s)

out = {"generated": date.today().isoformat(), "contexts": [c["context"] for c in ctxs],
       "providers": len(cohort),
       "note": "Counts are providers (catalog duplicates and shared specifications folded), a provider can appear under several forms.",
       "measures": {dim: {v: len(s) for v, s in sorted(vals.items(), key=lambda kv: -len(kv[1]))}
                    for dim, vals in sorted(m.items())}}
yaml.safe_dump(out, open(HUB / "evidence" / "naming.yml", "w"), sort_keys=False)
print(yaml.safe_dump(out["measures"], sort_keys=False))
print(out["providers"], "providers across", out["contexts"])

# Render the ruleset from its template, so the counts its rules cite are never older than
# the evidence. Placeholders: {{providers}}, {{contexts}}, {{<measure>.<form>}}; any other
# {{...}} is Spectral's and is left alone.
tpl = (HUB / "ruleset" / "schema-commons-naming.template.yaml").read_text()
names = {c["context"]: c["name"] for c in ctxs}


def fill(m):
    key = m.group(1)
    if key == "providers":
        return str(out["providers"])
    if key == "contexts":
        return ", ".join(names[c] for c in out["contexts"])
    if "." not in key:
        return m.group(0)  # Spectral's own {{property}} / {{value}} message placeholders
    dim, form = key.split(".", 1)
    return str(out["measures"][dim][form])


(HUB / "ruleset" / "schema-commons-naming.yaml").write_text(re.sub(r"\{\{([^}]+)\}\}", fill, tpl))

# The hub README's rule table, from the same numbers.
M = out["measures"]
rows = [f"Measured across {', '.join(names[c] for c in out['contexts'])}: {out['providers']} providers.", "",
        "| Rule | Measured (providers) | Severity |", "| --- | --- | --- |",
        f"| path segments kebab-case | lowercase {M['path_segment']['lower']}; multi-word kebab {M['path_segment']['kebab-case']} / snake {M['path_segment']['snake_case']} / camel {M['path_segment']['camelCase']} | warn |",
        f"| timestamps end in `_at` | `_at` {M['timestamp']['_at']} / bare `created` {M['timestamp']['bare']} / `_time`, `_date`, `on` {M['timestamp']['_date/_time/on']} | warn |",
        f"| collections are plural | plural {M['collection_noun']['plural']} / singular {M['collection_noun']['singular']} | info |",
        f"| properties snake_case | multi-word snake {M['property']['snake_case']} / camel {M['property']['camelCase']} | info |",
        f"| references `<resource>_id` | `_id` {M['foreign_key']['_id']} / `...Id` {M['foreign_key']['Id']} | info |",
        f"| path params snake_case | `{{id}}` {M['path_param']['lower']}; multi-word camel {M['path_param']['camelCase']} / snake {M['path_param']['snake_case']} | info |",
        f"| query params snake_case | snake {M['query_param']['snake_case']} / camel {M['query_param']['camelCase']} | info |",
        f"| paging is `limit` + `cursor` | limit {M['pagination_param']['limit']}, page {M['pagination_param']['page']}, offset {M['pagination_param']['offset']}, cursor {M['pagination_param']['cursor']} | info |"]
readme = HUB / "README.md"
t = readme.read_text()
i, j = t.index("<!-- commons:naming -->"), t.index("<!-- /commons:naming -->")
readme.write_text(t[:i] + "<!-- commons:naming -->\n" + "\n".join(rows) + "\n" + t[j:])

# The hub README's context table, from contexts.yml and each built context's profile.
rows = ["| Context | Repo | Status | Providers measured | Crosswalks |", "| --- | --- | --- | ---: | ---: |"]
planned = []
for c in yaml.safe_load(open(HUB / "contexts.yml"))["contexts"]:
    if c["status"] == "planned":
        planned.append(c["name"])
        continue
    repo = HUB.parent / c["context"]
    prof = yaml.safe_load(open(repo / "profile.yml"))
    n_cw = len(list((repo / "crosswalk").glob("*.yml")))
    rows.append(f"| {c['name']} | [{c['repo']}](https://github.com/{c['repo']}) | {c['status']} | "
                f"{prof['cohort']['providers_with_harvested_openapi']} | {n_cw} |")
rows += ["", "Planned, in order: " + ", ".join(planned) + "."]
t = readme.read_text()
i, j = t.index("<!-- commons:contexts -->"), t.index("<!-- /commons:contexts -->")
readme.write_text(t[:i] + "<!-- commons:contexts -->\n" + "\n".join(rows) + "\n" + t[j:])
