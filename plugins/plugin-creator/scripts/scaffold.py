#!/usr/bin/env python3
"""Scaffold a new plugin that meets the marketplace standard.

Creates plugins/<name>/ in the Agent Plugins 1.0 format (root plugin.json, skills/, evals, README),
registers the plugin in .claude-plugin/marketplace.json, and adds a CODEOWNERS line.
Run scripts/sync_manifests.py (generates the Claude Code and Cursor files) and
scripts/build_catalog.py afterwards. Add agents or commands under com.github.copilot/ if needed.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
CATEGORIES = ["productivity", "development", "security", "observability"]
AP_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def find_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".claude-plugin" / "marketplace.json").exists() and (p / "plugins").is_dir():
            return p
    sys.exit("Run this from inside the marketplace repository.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--owner-name", required=True)
    ap.add_argument("--owner-email", required=True)
    ap.add_argument("--owner-handle", required=True, help="GitHub team, e.g. @your-org/your-team or @your-username")
    ap.add_argument("--category", required=True, choices=CATEGORIES)
    ap.add_argument("--skill", required=True)
    ap.add_argument("--skill-description", required=True)
    a = ap.parse_args()

    for value, label in ((a.name, "plugin name"), (a.skill, "skill name")):
        if not NAME_RE.match(value):
            sys.exit(f"Invalid {label} '{value}': use lowercase letters, digits and hyphens, max 64 chars.")

    root = find_root(Path.cwd())
    pdir = root / "plugins" / a.name
    market_path = root / ".claude-plugin" / "marketplace.json"
    market = json.loads(market_path.read_text(encoding="utf-8"))
    if pdir.exists() or any(p["name"] == a.name for p in market["plugins"]):
        sys.exit(f"Plugin '{a.name}' already exists.")

    # Agent Plugins 1.0 manifest
    pdir.mkdir(parents=True)
    manifest = {
        "$schema": AP_PLUGIN_SCHEMA,
        "name": a.name,
        "version": "0.1.0",
        "description": a.description,
        "author": {"name": a.owner_name, "email": a.owner_email},
        "license": "MIT",
        "keywords": [],
    }
    (pdir / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # First skill
    sdir = pdir / "skills" / a.skill
    for sub in ("steps", "references", "templates"):
        (sdir / sub).mkdir(parents=True)
        (sdir / sub / ".gitkeep").write_text("", encoding="utf-8")
    (sdir / "SKILL.md").write_text(f"""---
name: {a.skill}
description: {a.skill_description}
---

# {a.skill.replace('-', ' ').capitalize()}

TODO: one paragraph on what this skill does.

## When to use

- TODO

## When not to use

- TODO

## Inputs and prerequisites

- TODO

## Workflow

1. TODO: link each step file, for example steps/01-discover.md, and say when to load it.

## Safety boundaries and stop conditions

- TODO: what this skill must never do, and when it stops.

## Outputs and completion

- TODO: what it produces, and how you know it is done.
""", encoding="utf-8")

    # Evals
    (pdir / "evals").mkdir()
    (pdir / "evals" / "evals.yaml").write_text(f"""# Eval cases for {a.name}. At least 10 cases are required, including trigger cases.
plugin: {a.name}
cases:
  - id: trigger-example
    type: trigger
    prompt: "TODO: a prompt that should trigger {a.skill}"
    expect: {{ skill: {a.skill}, triggered: true }}
""", encoding="utf-8")

    # README
    (pdir / "README.md").write_text(f"""# {a.name}

{a.description}

| | |
| --- | --- |
| **Owner** | {a.owner_name} (`{a.owner_handle}`) |
| **Status** | Beta (`0.x`) |
| **Format** | Agent Plugins 1.0 (Claude Code and Cursor files generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |

## Install

```text
/plugin install {a.name} --marketplace <owner>/<repo>
```

## Usage

TODO
""", encoding="utf-8")

    # Register
    market["plugins"].append({
        "name": a.name,
        "source": f"./plugins/{a.name}",
        "description": a.description,
        "category": a.category,
    })
    market_path.write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    codeowners = root / ".github" / "CODEOWNERS"
    with codeowners.open("a", encoding="utf-8") as f:
        f.write(f"/plugins/{a.name}/ {a.owner_handle}\n")

    print(f"Created plugins/{a.name}/ and registered it.")
    print("Next: python3 scripts/sync_manifests.py && python3 scripts/build_catalog.py && python3 scripts/validate_repo.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
