#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check a context's prose findings against its measured profile.

Findings are written by hand and cite measurements. Every improvement to the census can make
one wrong, and in the first batch about twenty went stale unnoticed. This reads the claim
patterns findings actually use and checks each against profile.yml and the crosswalks:

  "agrees on A, B and C"       every listed property must be core in a concept the finding names
  "agrees only on A and B"     ... and the core must be exactly those
  "`prop` (NN%)" / "prop NN%"  the share must be within 2 points
  "(N providers)"              must match providers_exposing of a named concept (within 1)
  Capitalised provider names   a catalog provider named here must appear in the crosswalks

It cannot judge meaning; it catches drift. Usage, from the hub:
  check-findings.py <context> [<context> ...] | --all   [--strict]
--strict exits 1 when anything drifted, so context.sh finish can refuse to commit.
"""
import argparse, glob, re, sys
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
COMMONS = HUB.parent
ALL = Path("/Users/kinlane/Github/all")

ap = argparse.ArgumentParser()
ap.add_argument("contexts", nargs="*")
ap.add_argument("--all", action="store_true")
ap.add_argument("--strict", action="store_true")
a = ap.parse_args()
if a.all:
    a.contexts = [c["context"] for c in yaml.safe_load(open(HUB / "contexts.yml"))["contexts"] if c["status"] != "planned"]


def snake(n):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", n))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def slug(n):
    return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")


# Capitalised words in findings that are standards, formats or ordinary words, not providers.
NOT_PROVIDERS = {"OpenAPI", "GraphQL", "RBAC", "RESO", "OSRM", "OTLP", "Open Banking", "Issues", "Questions",
                 "Current", "Once", "Balance", "Monday", "Wave", "FIX", "SCIM", "FHIR", "NPI", "CAP", "ActivityPub", "LTI", "OneRoster", "OCPI", "OCPP", "CDR",
                 "JSON", "XML", "REST", "HTTP", "SDK", "SDKs", "API", "APIs", "URL", "CSV", "PDF", "HTML", "LLM", "AI", "OCR",
                 "MCP", "OAuth", "SSO", "SAML", "SIEM", "KMS", "TLS", "DNS", "CDN", "OTLP", "IoT", "EHR", "ERP", "CRM", "POS", "ITSM", "CMDB", "ITIL", "MDM", "SaaS", "B2B", "BNPL", "KYC", "AML", "HR", "LMS", "CMS", "PDF"}
SPLIT = re.compile(r",\s*(?:and\s+)?|\s+and\s+|\s*/\s*")
STOP = {"the", "a", "an", "its", "their", "whether", "when", "which", "what", "dates", "timestamps",
        "it", "them", "both", "one", "two", "three"}
# How findings say "these properties": map to canonical property names.
PHRASES = {"dates": ["created_at", "updated_at"], "timestamps": ["created_at", "updated_at"],
           "title": ["name"], "name": ["name"], "first and last name": ["first_name", "last_name"],
           "start and end": ["start_at", "end_at"], "start, end": ["start_at", "end_at"]}


def concepts_named(text, prof):
    hits = []
    for c in prof:
        words = {c, c.replace("_", " "), c.replace("_", " ") + "s", c + "s", c.split("_")[-1], c.split("_")[-1] + "s"}
        if any(re.search(rf"\b{re.escape(w)}\b", text, re.I) for w in words):
            hits.append(c)
    return hits or list(prof)


ALIASES = {}


def resolve_prop(token, concepts, prof):
    """A token in prose -> the canonical property name it refers to, if any. A multi-word
    token is tried whole, then by its leading words ("address across the providers")."""
    words = token.strip("`* .;:").split()
    for k in range(len(words), 0, -1):
        got = _resolve(" ".join(words[:k]), concepts, prof)
        if got:
            return got
    return None


def _resolve(token, concepts, prof):
    t = snake(re.sub(r"^(the|a|an|its|their)\s+", "", token.strip("`* .;:"), flags=re.I))
    if not t or t in STOP:
        return None
    if t not in {p["name"] for c in concepts for p in prof[c]["properties"]}:
        for c in concepts:
            if t in ALIASES.get(c, {}):
                t = ALIASES[c][t]
                break
    # An exact property name in any named concept wins over a recorded spelling of another.
    for c in concepts:
        for p in prof[c]["properties"]:
            if t == p["name"]:
                return p["name"]
    for c in concepts:
        for p in prof[c]["properties"]:
            if t in {snake(s) for s in p["spellings"]}:
                return p["name"]
    # long-tail or extended names are still properties, just not core
    for c in concepts:
        if t in prof[c].get("long_tail_sample", []):
            return t
    return None


def check(ctx):
    repo = COMMONS / ctx
    cfg = yaml.safe_load(open(repo / "concepts.yml"))
    prof = yaml.safe_load(open(repo / "profile.yml"))["concepts"]
    crosswalk = {Path(p).stem for p in glob.glob(str(repo / "crosswalk" / "*.yml"))}
    ALIASES.clear()
    # Aliases are per concept (a concept's own win over the common ones), as in build.py.
    for cname, cdef in cfg["concepts"].items():
        amap = {}
        for group in (cfg.get("common_fields") or {}, cdef.get("aliases") or {}):
            for canon, al in group.items():
                for x in al:
                    amap[snake(str(x))] = str(canon)
        ALIASES[cname] = amap
    # concepts measured and dropped are recorded in comments; counts about them are not drift
    raw_cfg = (repo / "concepts.yml").read_text()
    dropped = set(re.findall(r"#\s*([a-z_]+) (?:and [a-z_]+ )?was measured and dropped", raw_cfg))
    dropped |= set(re.findall(r"#\s*[a-z_]+, ([a-z_]+)", raw_cfg))
    dropped_words = {w for d in dropped for w in (d, d.replace("_", " "), d.split("_")[-1])}
    problems = []
    for f in cfg.get("findings") or []:
        text = " ".join(f.split())
        named = concepts_named(text, prof)
        core = {c: {p["name"] for p in prof[c]["properties"] if p["tier"] == "core"} for c in prof}
        share = {c: {p["name"]: p["share"] for p in prof[c]["properties"]} for c in prof}

        # "agrees (only) on A, B and C" -- up to the next dash, colon, semicolon or full stop.
        for m in re.finditer(r"agrees?\s+(only\s+|completely\s+|almost completely\s+)?on\s+([^.;:()—]+?)(?=\s--|[.;:(]|$)", text):
            only = bool(m.group(1) and "only" in m.group(1))
            raw = m.group(2)
            if re.match(r"(nothing|more|less|little)\b", raw):
                continue
            listed = set()
            for tok in SPLIT.split(raw):
                tok = tok.strip()
                if tok.lower() in PHRASES:
                    listed |= set(PHRASES[tok.lower()]); continue
                name = resolve_prop(tok, named, prof)
                if name:
                    listed.add(name)
            if not listed:
                continue
            # The claim holds if ANY concept the sentence names satisfies it.
            ok = [c for c in named if listed <= core[c] and (not only or not (core[c] - listed - {"id"}))]
            if not ok:
                best = max(named, key=lambda c: len(listed & core[c]))
                what = "ONLY " if only else ""
                problems.append(f"says `{best}` agrees {what}on {sorted(listed)}; core is {sorted(core[best])}")

        # "prop (NN%)" or "prop NN%" -- the nearest property before a percentage
        for m in re.finditer(r"`?([A-Za-z_][A-Za-z0-9_]*)`?\s*\(?\s*(\d{1,3})%", text):
            name = resolve_prop(m.group(1), named, prof)
            if not name:
                continue
            got = [round(share[c][name] * 100) for c in named if name in share[c]]
            if got and all(abs(g - int(m.group(2))) > 2 for g in got):
                problems.append(f"`{name}` {m.group(2)}% -- measured {got}%")

        # "(N providers)" next to a named concept
        for m in re.finditer(r"\((\d+) providers?\b", text):
            n = int(m.group(1))
            if any(re.search(rf"\b{re.escape(w)}", text, re.I) for w in dropped_words) or re.search(r"dropped|as a resource|thin", text):
                continue
            # the cohort size and the crosswalk count are legitimate counts too
            cohort = yaml.safe_load(open(repo / "profile.yml"))["cohort"]["providers_with_harvested_openapi"]
            if n in (cohort, len(crosswalk)):
                continue
            if not any(abs(prof[c]["providers_exposing"] - n) <= 1 for c in named):
                problems.append(f"({n} providers) -- concepts named expose {[prof[c]['providers_exposing'] for c in named]}")

        # Capitalised names that are catalog providers must be in this context's crosswalks
        absent = re.search(r"absent|publish(es)? no|publishes none|no harvested|not in (this cohort|the catalog)|GraphQL|keep their APIs|partner-gated|private", text, re.I)
        for m in ([] if absent else re.finditer(r"\b([A-Z][A-Za-z0-9]+(?:[ .][A-Z][A-Za-z0-9]+)?)\b", text)):
            if m.group(1) in NOT_PROVIDERS or any(w in NOT_PROVIDERS for w in re.split(r"[ .]", m.group(1))):
                continue
            # a single capitalised word opening a sentence is ordinary English ("Every", "Most")
            before = text[:m.start()].rstrip()
            if " " not in m.group(1) and (not before or before[-1] in ".:;!?\"-"):
                continue
            s = slug(m.group(1))
            if s in (cfg.get("shared_specs") or {}) or any(s in k for k in (cfg.get("shared_specs") or {})):
                continue  # a shared standard's voice is named for the standard, not a crosswalk
            flat = {x.replace("-", "") for x in crosswalk}
            if len(s) > 3 and (ALL / s).is_dir() and s not in crosswalk and not any(s in x for x in crosswalk) \
                    and s.replace("-", "") not in flat:
                problems.append(f"names {m.group(1)}, which has no crosswalk in this context")
    return problems


total = 0
for ctx in a.contexts:
    probs = check(ctx)
    total += len(probs)
    for p in probs:
        print(f"{ctx}: {p}")
print(f"{total} finding claims drifted across {len(a.contexts)} contexts", file=sys.stderr)
sys.exit(1 if a.strict and total else 0)
