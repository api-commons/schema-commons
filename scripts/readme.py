#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Write a context's README from concepts.yml (name, intro, cohort_note, findings,
decisions) and its profile. Run from the context repo; build.py then fills the measured
table between the summary markers. The decisions live in concepts.yml so that one report
can gather every context's calls (scripts/report.py)."""
import yaml

cfg = yaml.safe_load(open("concepts.yml"))
ctx, name = cfg["context"], cfg["name"]
bullets = lambda items: "\n".join(f"- {d.strip()}" for d in items)
findings = cfg.get("findings") or []
text = f"""# {name}

{cfg['intro'].strip()} Part of [Schema Commons](https://github.com/api-commons/schema-commons),
published by the [API Commons](https://apicommons.org).

Built from the providers tagged {', '.join(map(str, cfg['tags']))} in [APIs.io](https://apis.io) that
publish their own OpenAPI. Only harvested contracts count -- nothing API Evangelist
generated. Every number below is a count of providers.

## What the market already agrees on

<!-- commons:summary -->
<!-- /commons:summary -->

Shares are of the providers with a readable resource schema for that concept. The
extended tier and the long tail of every concept are in [profile.yml](profile.yml).
"""
if findings:
    text += "\n## What the measurement shows\n\n" + bullets(findings) + "\n"
import glob as _g
std_files = sorted(_g.glob("standards/*.yml"))
if std_files:
    text += "\n## Measured against the standard\n\n"
    text += ("The census reads what providers publish. Where the domain has a standard, the standard's own\n"
             "definition is read as one more voice: how much of the measured core it defines, and what it\n"
             "defines that no provider in the cohort publishes. Crosswalks are in [standards/](standards).\n\n")
    text += "| Standard | Concept | Core defined by the standard | Fields only the standard has |\n| --- | --- | ---: | ---: |\n"
    for f in std_files:
        r = yaml.safe_load(open(f))
        for c, v in r["concepts"].items():
            text += f"| [{r['standard']}]({r['source']}) | `{c}` | {('no measured core' if v['core_coverage'] is None else format(v['core_coverage'], '.0%'))} | {len(v['standard_only'])} |\n"
        for c, v in (r.get("defines_unpublished") or {}).items():
            text += f"| [{r['standard']}]({r['source']}) | `{c}` *(not published by the market)* | -- | {len(v['fields'])} |\n"
text += f"""
## Artifacts

- [openapi.yml](openapi.yml) -- OpenAPI 3.1 of the shared operations. No one serves it; it
  is the shape to map to. Lints clean against the
  [naming ruleset](https://github.com/api-commons/schema-commons/blob/main/ruleset/schema-commons-naming.yaml).
{"- [arazzo.yml](arazzo.yml) -- reference workflows composed only of the shared operations (compositions, not measurements)." + chr(10) if __import__("os").path.exists("arazzo.yml") else ""}- [schema/](schema) -- JSON Schema 2020-12 per concept; each property carries
  `x-commons-tier`, `x-commons-share`, `x-commons-providers` and the spellings seen.
- [crosswalk/](crosswalk) -- one per provider, common name -> their name, with the harvested
  spec and operations each mapping was read from.
- [adopters.yml](adopters.yml) -- who exposes which concept, linked to their APIs.io page.
- [concepts.yml](concepts.yml) -- the only hand-written input: concepts, path segments and
  their qualifiers, aliases, reviewed exclusions, merged duplicates, and the decisions below.
- [census/](census) -- the cohort and the raw census the profile is built from.

## Decisions

These are calls, not measurements, recorded so they can be revisited as the method matures.

{bullets(cfg.get('decisions') or [])}

## Rebuild

```bash
../schema-commons/scripts/run.sh .
```

## License

Artifacts CC BY-NC-SA 4.0 ([LICENSE](LICENSE)); code Apache 2.0 ([LICENSE-CODE](LICENSE-CODE)).
"""
open("README.md", "w").write(text)
