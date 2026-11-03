#!/usr/bin/env python3
"""Build catalog.json (a machine-readable index of every plugin, skill, agent and command)
and refresh the plugins table in README.md.

catalog.json is what the duplicate check and Copilot review read to spot overlap.
Usage:
  python3 scripts/build_catalog.py           # write files
  python3 scripts/build_catalog.py --check   # fail if out of date (CI)
"""
from __future__ import annotations

import argparse
import sys

from marketplace_lib import (
    CATALOG,
    COPILOT_NS,
    CLAUDE_MARKETPLACE,
    README,
    dump_json,
    load_json,
    plugin_dir,
    read_frontmatter,
)

TABLE_START = "<!-- plugins-table:start -->"
TABLE_END = "<!-- plugins-table:end -->"


def build_catalog() -> dict:
    market = load_json(CLAUDE_MARKETPLACE)
    plugins = []
    for entry in sorted(market["plugins"], key=lambda e: e["name"]):
        pdir = plugin_dir(entry)
        manifest_path = pdir / "plugin.json"  # Agent Plugins manifest
        manifest = load_json(manifest_path) if manifest_path.exists() else {}

        skills = []
        for skill_md in sorted(pdir.glob("skills/*/SKILL.md")):
            fm = read_frontmatter(skill_md) or {}
            skills.append({"name": fm.get("name", skill_md.parent.name), "description": fm.get("description", "")})

        agents = []
        for agent_md in sorted(pdir.glob(f"{COPILOT_NS}/agents/*.agent.md")):
            fm = read_frontmatter(agent_md) or {}
            default = agent_md.name.removesuffix(".agent.md")
            agents.append({"name": fm.get("name", default), "description": fm.get("description", "")})

        commands = []
        for cmd_md in sorted(pdir.glob(f"{COPILOT_NS}/commands/*.md")):
            fm = read_frontmatter(cmd_md) or {}
            commands.append({"name": cmd_md.stem, "description": fm.get("description", "")})

        plugins.append({
            "name": entry["name"],
            "version": manifest.get("version", ""),
            "description": entry.get("description") or manifest.get("description", ""),
            "category": entry.get("category", ""),
            "owner": manifest.get("author", {}).get("name", ""),
            "skills": skills,
            "agents": agents,
            "commands": commands,
        })
    return {"marketplace": market["name"], "plugins": plugins}


def render_table(catalog: dict) -> str:
    rows = [
        "| Plugin | Version | Category | Owner | Skills | Description |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for p in catalog["plugins"]:
        skills = ", ".join(f"`{s['name']}`" for s in p["skills"]) or "none"
        rows.append(
            f"| [`{p['name']}`](plugins/{p['name']}/) | {p['version']} | {p['category']} "
            f"| {p['owner']} | {skills} | {p['description']} |"
        )
    return "\n".join(rows)


def updated_readme(catalog: dict) -> str:
    text = README.read_text(encoding="utf-8")
    start, end = text.find(TABLE_START), text.find(TABLE_END)
    if start == -1 or end == -1:
        return text
    return text[: start + len(TABLE_START)] + "\n" + render_table(catalog) + "\n" + text[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    catalog = build_catalog()
    targets = {CATALOG: dump_json(catalog), README: updated_readme(catalog)}

    stale = []
    for path, content in targets.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            if args.check:
                stale.append(path.name)
            else:
                path.write_text(content, encoding="utf-8")
                print(f"wrote    {path.name}")

    if args.check:
        if stale:
            print(f"Out of date: {', '.join(stale)}. Run: python3 scripts/build_catalog.py")
            return 1
        print("catalog.json and README plugins table are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
