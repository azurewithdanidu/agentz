#!/usr/bin/env python3
"""Generate the client-specific manifest copies from each plugin's source files.

Plugins use the classic layout that VS Code (Copilot), Copilot CLI and Claude Code all read,
so agents, commands and skills exist once. Only manifests and marketplace files are generated.

Sources you edit (per plugin):
  plugin.json                      manifest (name, version, description, author, ...)
  .mcp.json                        MCP servers (optional), read by Copilot and Claude Code
  skills/<name>/SKILL.md           skills, read by every client as-is
  agents/<name>.agent.md           agents, read by Copilot and Claude Code
  commands/<name>.md               slash commands, read by Claude Code (and Copilot where supported)

Generated (never edit by hand):
  .claude-plugin/plugin.json       Claude Code manifest (Claude only reads this path)
  .cursor-plugin/plugin.json       Cursor manifest
  mcp.json                         Cursor copy of .mcp.json
and at the repo root:
  .github/plugin/marketplace.json  Copilot CLI / VS Code marketplace (documented location)
  .cursor-plugin/marketplace.json  Cursor marketplace

Usage:
  python3 scripts/sync_manifests.py           # write files
  python3 scripts/sync_manifests.py --check   # fail if anything is out of date (CI)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from marketplace_lib import (
    CLAUDE_MARKETPLACE,
    COPILOT_MARKETPLACE,
    CURSOR_MARKETPLACE,
    ROOT,
    dump_json,
    load_json,
    plugin_dir,
)

MANIFEST_FIELDS = ["name", "version", "description", "author", "homepage", "repository", "license", "keywords"]
CURSOR_ENTRY_FIELDS = ["name", "source", "description", "version", "category", "tags", "keywords"]


def plugin_files(pdir: Path) -> dict[Path, str | None]:
    files: dict[Path, str | None] = {}
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

    # Cursor reads mcp.json (no dot); the source is .mcp.json
    mcp = pdir / ".mcp.json"
    files[pdir / "mcp.json"] = mcp.read_text(encoding="utf-8") if mcp.exists() else None
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
        print("All generated files are in sync with the plugin sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
