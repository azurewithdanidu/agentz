#!/usr/bin/env python3
"""Generate the Cursor mirror from the Claude manifests (the source of truth).

Writes:
  .cursor-plugin/marketplace.json            from .claude-plugin/marketplace.json
  plugins/<p>/.cursor-plugin/plugin.json     from plugins/<p>/.claude-plugin/plugin.json
  plugins/<p>/mcp.json                       from plugins/<p>/.mcp.json (Cursor and Agent Plugins name)

Never edit the generated files by hand. Usage:
  python3 scripts/sync_manifests.py           # write files
  python3 scripts/sync_manifests.py --check   # fail if anything is out of date (CI)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from marketplace_lib import (
    CLAUDE_MARKETPLACE,
    CURSOR_MARKETPLACE,
    ROOT,
    dump_json,
    load_json,
    plugin_dir,
)

# Fields Cursor documents for .cursor-plugin/plugin.json. Anything else is dropped.
CURSOR_PLUGIN_FIELDS = [
    "name", "description", "version", "author", "homepage",
    "repository", "license", "keywords", "logo",
]
CURSOR_ENTRY_FIELDS = ["name", "source", "description", "version", "category", "tags", "keywords"]


def expected_files() -> dict[Path, str | None]:
    """Map each generated path to its expected content (None means it should not exist)."""
    files: dict[Path, str | None] = {}
    market = load_json(CLAUDE_MARKETPLACE)

    cursor_market = {
        "name": market["name"],
        "owner": {k: v for k, v in market["owner"].items() if k in ("name", "email")},
        "metadata": {"description": market.get("description", "")},
        "plugins": [],
    }
    for entry in market["plugins"]:
        cursor_entry = {k: entry[k] for k in CURSOR_ENTRY_FIELDS if k in entry}
        # Cursor's documented examples use a plain relative path.
        cursor_entry["source"] = entry["source"].removeprefix("./")
        cursor_market["plugins"].append(cursor_entry)

        pdir = plugin_dir(entry)
        claude_manifest = pdir / ".claude-plugin" / "plugin.json"
        if claude_manifest.exists():
            manifest = load_json(claude_manifest)
            cursor_manifest = {k: manifest[k] for k in CURSOR_PLUGIN_FIELDS if k in manifest}
            if "author" in cursor_manifest:
                cursor_manifest["author"] = {
                    k: v for k, v in cursor_manifest["author"].items() if k in ("name", "email")
                }
            files[pdir / ".cursor-plugin" / "plugin.json"] = dump_json(cursor_manifest)

        claude_mcp = pdir / ".mcp.json"
        files[pdir / "mcp.json"] = dump_json(load_json(claude_mcp)) if claude_mcp.exists() else None

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
            print("Generated manifests are out of date. Run: python3 scripts/sync_manifests.py")
            for s in stale:
                print(f"  - {s}")
            return 1
        print("Cursor mirror and mcp.json files are in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
