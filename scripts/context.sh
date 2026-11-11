#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# One context, end to end, after its concepts.yml is written:
#   context.sh run <ctx>      cohort -> census -> build -> lint, then duplicates + review
#   context.sh finish <ctx>   README from concepts.yml, rebuild, index, lint, local commit
#   context.sh thin <ctx>     findings checked, measurement recorded in the hub (thin/), no repo
#   context.sh reference <ctx>  a standard owns the shape: its objects + who implements them (reference.py)
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HUB/../$2"
[ -f LICENSE ] || cp "$HUB/LICENSE" "$HUB/LICENSE-CODE" .
q() { grep -v -i -E "deprecat|npm warn|trace-dep|^$" || true; }
case "$1" in
  run)
    "$HUB/scripts/run.sh" . 2>&1 | q | grep -E "providers,|could not|exp /|crosswalks|problem|warning|error|Error|Traceback|line [0-9]" || true
    echo "-- duplicates"; python3 "$HUB/scripts/duplicates.py" 2>&1 | grep -v "already merged" | grep -v -E "^(aib|bank-of-ireland)" | head -12
    echo "-- review"; python3 "$HUB/scripts/review.py" --max "${MAX:-25}" ;;
  finish)
    # Always re-census: a renamed concept is otherwise silently empty in the build.
    python3 "$HUB/scripts/census.py" --cohort census/cohort.json 2>&1 | grep -E "Traceback|Error" || true
    rm -rf schema
    python3 "$HUB/scripts/readme.py"
    python3 "$HUB/scripts/build.py" 2>&1 | tail -1
    python3 "$HUB/scripts/arazzo.py"
    python3 "$HUB/scripts/overlay.py" | grep -v "none$" || true
    python3 "$HUB/scripts/apisjson.py"
    # Findings cite measurements; refuse to commit a context whose findings have drifted.
    python3 "$HUB/scripts/check-findings.py" "$2" --strict || { echo "findings drifted -- fix concepts.yml findings, then finish again"; exit 1; }
    npx --yes @stoplight/spectral-cli@6.15.0 lint openapi.yml -r "$HUB/ruleset/schema-commons-naming.yaml" --fail-severity=info 2>&1 | q | tail -1
    [ -d .git ] || git init -q -b main
    git add -A . && git commit -q -m "Schema Commons: $(python3 -c "import yaml;print(yaml.safe_load(open('concepts.yml'))['name'])") context

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git log --oneline -1
    python3 - "$HUB/contexts.yml" "$2" <<'PY'
import sys, yaml, re
p, ctx = sys.argv[1], sys.argv[2]
s = open(p).read()
s = re.sub(rf"(- context: {re.escape(ctx)}\n  name: [^\n]*\n  status:) planned", rf"\1 built\n  repo: api-commons/{ctx}", s)
open(p, "w").write(s)
PY
    ;;
  thin)
    # Measured and not published: no repo. The record lives in the hub (thin/<ctx>/), because
    # a context folder outside git is lost with the machine. Findings are checked like any other.
    python3 "$HUB/scripts/check-findings.py" "$2" --strict || { echo "findings drifted -- fix concepts.yml findings, then thin again"; exit 1; }
    mkdir -p "$HUB/thin/$2" && cp concepts.yml profile.yml "$HUB/thin/$2/"
    python3 - "$HUB/contexts.yml" "$2" <<'PY'
import sys, re
p, ctx = sys.argv[1], sys.argv[2]
s = open(p).read()
s = re.sub(rf"(- context: {re.escape(ctx)}\n  name: [^\n]*\n  status:) planned", r"\1 thin", s)
open(p, "w").write(s)
PY
    echo "thin: $2 (recorded in thin/$2)" ;;
  reference)
    # A standard owns the shape: publish its objects, measure who implements them (reference.py).
    python3 -c "import yaml;print('\n'.join(str(t) for t in yaml.safe_load(open('concepts.yml'))['tags']))" > census/tags.txt
    TAGS=(); while IFS= read -r t; do TAGS+=("$t"); done < census/tags.txt
    python3 "$HUB/scripts/cohort.py" --tags "${TAGS[@]}" --out census/cohort.json | tail -1
    python3 "$HUB/scripts/reference.py"
    python3 "$HUB/scripts/check-findings.py" "$2" --strict || { echo "findings drifted -- fix concepts.yml findings, then reference again"; exit 1; }
    [ -d .git ] || git init -q -b main
    git add -A . && git commit -q -m "Schema Commons: $(python3 -c "import yaml;print(yaml.safe_load(open('concepts.yml'))['name'])") reference context

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git log --oneline -1
    python3 - "$HUB/contexts.yml" "$2" <<'PY'
import sys, re
p, ctx = sys.argv[1], sys.argv[2]
s = open(p).read()
s = re.sub(rf"(- context: {re.escape(ctx)}\n  name: [^\n]*\n  status:) planned", rf"\1 reference\n  repo: api-commons/{ctx}", s)
open(p, "w").write(s)
PY
    ;;
esac
