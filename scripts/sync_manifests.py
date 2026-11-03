#!/usr/bin/env python3
"""Generate every client-specific file from the Agent Plugins 1.0 sources.

Sources you edit (per plugin):
  plugin.json                                  Agent Plugins manifest (VS Code, Copilot CLI, Copilot app)
  mcp.json                                     Agent Plugins MCP config (also read by Cursor)
  skills/<name>/SKILL.md                       portable skills, read by every client as-is
  com.github.copilot/agents/<name>.agent.md    custom agents for VS Code / Copilot
  com.github.copilot/commands/<name>.md        slash commands for VS Code / Copilot

Generated (never edit by hand):
  .claude-plugin/plugin.json                   Claude Code manifest
  .mcp.json                                    Claude Code MCP config ("streamable-http" -> "http")
  agents/<name>.md                             Claude Code agents (Copilot tool sets mapped to Claude tools)
  commands/<name>.md                           Claude Code commands
  .cursor-plugin/plugin.json                   Cursor manifest
and at the repo root:
  .github/plugin/marketplace.json              Copilot CLI / VS Code marketplace (documented location)
  .cursor-plugin/marketplace.json              Cursor marketplace

Usage:
  python3 scripts/sync_manifests.py           # write files
  python3 scripts/sync_manifests.py --check   # fail if anything is out of date (CI)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from marketplace_lib import (
    CLAUDE_MARKETPLACE,
    COPILOT_MARKETPLACE,
    COPILOT_NS,
    COPILOT_TO_CLAUDE_TOOLS,
    CURSOR_MARKETPLACE,
    ROOT,
    dump_json,
    load_json,
    plugin_dir,
    split_frontmatter,
)

MANIFEST_FIELDS = ["name", "version", "description", "author", "homepage", "repository", "license", "keywords"]
CURSOR_ENTRY_FIELDS = ["name", "source", "description", "version", "category", "tags", "keywords"]
GENERATED_DIRS = ("agents", "commands")


def banner(source: str) -> str:
    return f"<!-- GENERATED from {source} by scripts/sync_manifests.py. Do not edit. -->\n\n"


def frontmatter_md(fm: dict, body: str) -> str:
    dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10_000).strip()
    return f"---\n{dumped}\n---\n\n{body}"


def claude_tools(copilot_tools) -> str | None:
    if not copilot_tools:
        return None
    if isinstance(copilot_tools, str):
        copilot_tools = [t.strip() for t in copilot_tools.split(",")]
    out: list[str] = []
    for tool in copilot_tools:
        for mapped in COPILOT_TO_CLAUDE_TOOLS.get(str(tool), []):
            if mapped not in out:
                out.append(mapped)
    return ", ".join(out) if out else None


def plugin_files(pdir: Path) -> dict[Path, str | None]:
    files: dict[Path, str | None] = {}
    rel = lambda p: p.relative_to(pdir).as_posix()  # noqa: E731

    manifest_path = pdir / "plugin.json"
    if not manifest_path.exists():
        return files
    manifest = load_json(manifest_path)
    base = {k: manifest[k] for k in MANIFEST_FIELDS if k in manifest}

    # Claude Code manifest
    files[pdir / ".claude-plugin" / "plugin.json"] = dump_json(base)

    # Cursor manifest (documented fields only; author name/email only)
    cursor = dict(base)
    if "author" in cursor:
        cursor["author"] = {k: v for k, v in cursor["author"].items() if k in ("name", "email")}
    files[pdir / ".cursor-plugin" / "plugin.json"] = dump_json(cursor)

    # Claude Code MCP config
    mcp = pdir / "mcp.json"
    if mcp.exists():
        servers = {}
        for name, server in load_json(mcp).get("mcpServers", {}).items():
            server = dict(server)
            if server.get("type") == "streamable-http":
                server["type"] = "http"
            servers[name] = server
        files[pdir / ".mcp.json"] = dump_json({"mcpServers": servers})
    else:
        files[pdir / ".mcp.json"] = None

    # Claude Code agents and commands, generated from the Copilot namespace
    expected: set[Path] = set()
    ns = pdir / COPILOT_NS
    for src in sorted((ns / "agents").glob("*.agent.md")):
        fm, body = split_frontmatter(src)
        fm = dict(fm or {})
        name = fm.get("name") or src.name.removesuffix(".agent.md")
        claude_fm = {"name": name, "description": fm.get("description", "")}
        tools = claude_tools(fm.get("tools"))
        if tools:
            claude_fm["tools"] = tools
        target = pdir / "agents" / f"{name}.md"
        files[target] = frontmatter_md(claude_fm, banner(rel(src)) + body)
        expected.add(target)
    for src in sorted((ns / "commands").glob("*.md")):
        fm, body = split_frontmatter(src)
        target = pdir / "commands" / src.name
        files[target] = frontmatter_md(dict(fm or {}), banner(rel(src)) + body)
        expected.add(target)

    # Anything else in the generated folders is stale.
    for d in GENERATED_DIRS:
        for f in (pdir / d).glob("*") if (pdir / d).is_dir() else []:
            if f.is_file() and f not in expected:
                files[f] = None
    return files


def expected_files() -> dict[Path, str | None]:
    market = load_json(CLAUDE_MARKETPLACE)
    files: dict[Path, str | None] = {}

    # Copilot CLI / VS Code marketplace: same registry at the documented location.
    files[COPILOT_MARKETPLACE] = dump_json(market)

    cursor_market = {
        "name": market["name"],
        "owner": {k: v for k, v in market["owner"].items() if k in ("name", "email")},
        "metadata": {"description": market.get("description", "")},
        "plugins": [],
    }
    for entry in market["plugins"]:
        cursor_entry = {k: entry[k] for k in CURSOR_ENTRY_FIELDS if k in entry}
        cursor_entry["source"] = entry["source"].removeprefix("./")
        cursor_market["plugins"].append(cursor_entry)
        files.update(plugin_files(plugin_dir(entry)))
    files[CURSOR_MARKETPLACE] = dump_json(cursor_market)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if generated files are out of date")
    args = parser.parse_args()

    stale: list[str] = []
    for path, content in expected_files().items():
        rel = path.relative_to(ROOT)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(str(rel))
        elif content is None:
            path.unlink()
            print(f"removed  {rel}")
            if path.parent.is_dir() and not any(path.parent.iterdir()):
                path.parent.rmdir()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote    {rel}")

    if args.check:
        if stale:
            print("Generated files are out of date. Run: python3 scripts/sync_manifests.py")
            for s in stale:
                print(f"  - {s}")
            return 1
        print("All generated files are in sync with the Agent Plugins sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
