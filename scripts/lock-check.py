#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Report, per context, whether it meets the lock criteria in the hub README (Versioning).

  1 method stable    the hub's scripts/ unchanged across the context's last two rebuild commits
  2 reviewed         a Decisions section (or decisions:), and findings that pass check-findings.py
  3 ruleset settled  the naming ruleset is accepted into OpenLint (LOCK_RULESET_ACCEPTED=1, a hub-wide fact)
  4 rendered         the context's page is live on apis.io (HTTP 200 at /common-schema/<ctx>/)

Locking stays a decision, not an automatic step: this only says which criteria hold.
Usage: lock-check.py [<context> ...]   (default: every built context)"""
import os, subprocess, sys, urllib.request
from pathlib import Path
import yaml

HUB = Path(__file__).resolve().parent.parent
COMMONS = HUB.parent
registry = yaml.safe_load(open(HUB / "contexts.yml"))["contexts"]
ctxs = sys.argv[1:] or [c["context"] for c in registry if c["status"] in ("built", "published")]


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout.strip()


def method_stable(ctx):
    """The two most recent rebuild commits of the context; scripts/ must not have changed between them
    or since the later one."""
    dates = git(COMMONS / ctx, "log", "-2", "--format=%cI").splitlines()
    if len(dates) < 2:
        return False, "fewer than two rebuilds"
    changed = git(HUB, "log", "--format=%h", f"--since={dates[1]}", "--", "scripts")
    return (not changed), ("scripts unchanged since " + dates[1][:10]) if not changed else \
        f"{len(changed.splitlines())} script commits since the earlier rebuild"


def reviewed(ctx):
    cfg = yaml.safe_load(open(COMMONS / ctx / "concepts.yml"))
    readme = (COMMONS / ctx / "README.md").read_text()
    has = bool(cfg.get("decisions")) or "## Decisions" in readme
    ok = subprocess.run([sys.executable, str(HUB / "scripts" / "check-findings.py"), ctx, "--strict"],
                        capture_output=True).returncode == 0
    return has and ok, ("decisions recorded" if has else "no decisions") + (", findings clean" if ok else ", findings drifted")


def rendered(ctx):
    try:
        with urllib.request.urlopen(f"https://apis.io/common-schema/{ctx}/", timeout=10) as r:
            return r.status == 200, f"HTTP {r.status}"
    except Exception as e:
        return False, getattr(e, "code", None) and f"HTTP {e.code}" or "not reachable"


ruleset = os.environ.get("LOCK_RULESET_ACCEPTED") == "1"
print(f"criterion 3, ruleset settled: {'yes' if ruleset else 'no'} (hub-wide; set LOCK_RULESET_ACCEPTED=1 once accepted)")
print(f"{'context':28} {'1 method':>9} {'2 reviewed':>11} {'4 rendered':>11}  ready")
ready = []
for ctx in ctxs:
    r = [method_stable(ctx), reviewed(ctx), rendered(ctx)]
    ok = all(x[0] for x in r) and ruleset
    if ok:
        ready.append(ctx)
    print(f"{ctx:28} {'yes' if r[0][0] else 'no':>9} {'yes' if r[1][0] else 'no':>11} {'yes' if r[2][0] else 'no':>11}  "
          f"{'READY' if ok else ''}   {'; '.join(x[1] for x in r)}")
print(f"{len(ready)} of {len(ctxs)} ready to lock")
