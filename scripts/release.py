#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Lock and release a context, as the hub README's Versioning section describes.

  release.py <ctx> <version>    freeze the contract at <version> and tag it
  release.py <ctx> --diff       compare the live measurement with the released contract

A release copies schema/<concept>.json to schema/v<major>/<concept>.json with a versioned $id,
stamps version and status: stable, records `release:` in concepts.yml (build.py then stamps
that version instead of a dated draft), writes CHANGELOG.md, commits and tags v<version> in
the context repo. It refuses unless lock-check.py reports the context ready; locking is a
decision, so RELEASE_OVERRIDE=<reason> records a deliberate exception in the changelog.

After release, every build re-measures the live schema/. --diff reports what moved against
the released contract: a property promoted to core is a candidate for the next minor, a core
property that fell below its tier is a demotion, reported now and applied only at the next major.
Measurements (profile, adopters, crosswalks) are data and are never versioned."""
import json, os, re, subprocess, sys
from datetime import date
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
ctx, arg = sys.argv[1], sys.argv[2]
repo = HUB.parent / ctx
cfg_p = repo / "concepts.yml"
cfg = yaml.safe_load(open(cfg_p))


def core(schema):
    return {k for k, v in (schema.get("properties") or {}).items() if v.get("x-commons-tier") == "core"}


if arg == "--diff":
    rel = (cfg.get("release") or {}).get("version")
    if not rel:
        sys.exit(f"{ctx} has no release yet")
    vdir = repo / "schema" / f"v{rel.split('.')[0]}"
    for live in sorted((repo / "schema").glob("*.json")):
        frozen = vdir / live.name
        if not frozen.exists():
            print(f"{live.stem}: new concept since {rel} -- minor")
            continue
        a, b = core(json.load(open(frozen))), core(json.load(open(live)))
        for p in sorted(b - a):
            print(f"{live.stem}.{p}: promoted to core -- candidate for the next minor")
        for p in sorted(a - b):
            print(f"{live.stem}.{p}: fell below core -- demotion, report now, apply at the next major")
    sys.exit(0)

version = arg
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    sys.exit("version must be MAJOR.MINOR.PATCH")
override = os.environ.get("RELEASE_OVERRIDE")
chk = subprocess.run([sys.executable, str(HUB / "scripts" / "lock-check.py"), ctx], capture_output=True, text=True,
                     env={**os.environ})
if "1 of 1 ready" not in chk.stdout and not override:
    sys.exit(chk.stdout + f"\n{ctx} is not ready to lock. Set RELEASE_OVERRIDE='<reason>' to record a deliberate exception.")

major = version.split(".")[0]
raw = f"https://raw.githubusercontent.com/api-commons/{ctx}/v{version}"
vdir = repo / "schema" / f"v{major}"
vdir.mkdir(exist_ok=True)
for f in sorted((repo / "schema").glob("*.json")):
    s = json.load(open(f))
    s["$id"] = f"{raw}/schema/v{major}/{f.name}"
    s.setdefault("x-commons", {}).update({"version": version, "status": "stable"})
    json.dump(s, open(vdir / f.name, "w"), indent=2)

text = cfg_p.read_text()
text = re.sub(r"\nrelease:\n(  .*\n)*", "\n", text).rstrip("\n")
text += f"\nrelease:\n  version: {version}\n  date: {date.today().isoformat()}\n"
cfg_p.write_text(text)

log = repo / "CHANGELOG.md"
entry = [f"## {version} -- {date.today().isoformat()}", "",
         f"Contract frozen at `schema/v{major}/`: " + ", ".join(f"`{f.stem}`" for f in sorted(vdir.glob('*.json'))) + ".",
         "Measurements (profile, adopters, crosswalks) continue to refresh and are not versioned."]
if override:
    entry.append(f"Released before every lock criterion held: {override}")
prev = log.read_text().split("\n", 2)[2] if log.exists() else ""
log.write_text("# Changelog\n\n" + "\n".join(entry) + "\n\n" + prev)

subprocess.run(["git", "-C", str(repo), "add", "concepts.yml", "CHANGELOG.md", f"schema/v{major}"], check=True)
subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m",
                f"Release {version}: contract frozen at schema/v{major}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"],
               check=True)
subprocess.run(["git", "-C", str(repo), "tag", "-a", f"v{version}", "-m", f"{cfg['name']} {version}"], check=True)
print(f"{ctx} {version}: tagged v{version}; push the tag with the repository")
