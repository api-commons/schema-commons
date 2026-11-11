#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Rebuild one bounded context end to end: cohort -> census -> profile, schema, OpenAPI,
# crosswalks -> lint the common OpenAPI against the naming ruleset (must be clean).
# Usage: run.sh <path to context repo>     e.g. run.sh ../crm
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
cd "$1"
TAGS=$(python3 -c "import yaml;print('\n'.join(yaml.safe_load(open('concepts.yml'))['tags']))")
mkdir -p census

IFS=$'\n' read -r -d "" -a T <<< "$TAGS" || true
python3 "$HUB/scripts/cohort.py" --tags "${T[@]}" --out census/cohort.json
python3 "$HUB/scripts/census.py" --cohort census/cohort.json
python3 "$HUB/scripts/build.py"
npx --yes @stoplight/spectral-cli@6.15.0 lint openapi.yml -r "$HUB/ruleset/schema-commons-naming.yaml" --fail-severity=info
