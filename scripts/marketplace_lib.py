"""Shared helpers for the marketplace scripts. Requires PyYAML."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"   # registry: source of truth
COPILOT_MARKETPLACE = ROOT / ".github" / "plugin" / "marketplace.json"  # generated
CURSOR_MARKETPLACE = ROOT / ".cursor-plugin" / "marketplace.json"       # generated
CATALOG = ROOT / "catalog.json"
README = ROOT / "README.md"
CODEOWNERS = ROOT / ".github" / "CODEOWNERS"

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
CATEGORIES = {"productivity", "development", "security", "observability"}

# Agent Plugins 1.0 (https://agent-plugins.org) is the source format for every plugin.
AP_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AP_MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
AP_PLUGIN_FIELDS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
AP_MCP_TYPES = {"stdio", "streamable-http", "sse"}
COPILOT_NS = "com.github.copilot"   # VS Code, Copilot CLI and the Copilot app read agents/commands/rules/hooks here

# Copilot tool sets -> Claude Code tools, used to generate Claude agents from Copilot agents.
COPILOT_TO_CLAUDE_TOOLS = {
    "read": ["Read"],
    "search": ["Grep", "Glob"],
    "edit": ["Edit", "Write"],
    "execute": ["Bash"],
    "web": ["WebFetch", "WebSearch"],
    "todo": ["TodoWrite"],
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def dump_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def plugin_dir(entry: dict) -> Path:
    return (ROOT / entry["source"]).resolve()


def split_frontmatter(path: Path) -> tuple[dict | None, str]:
    """Return (frontmatter, body) for a Markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    data = yaml.safe_load(parts[1])
    return (data if isinstance(data, dict) else None), parts[2].lstrip("\n")


def read_frontmatter(path: Path) -> dict | None:
    """Return the YAML frontmatter of a Markdown file, or None if it has none."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else None


def semver_tuple(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split("-", 1)[0].split(".")
    return int(major), int(minor), int(patch)


class Reporter:
    """Collects errors and warnings, and prints GitHub annotations in Actions."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.in_actions = os.environ.get("GITHUB_ACTIONS") == "true"

    def error(self, msg: str, file: Path | str | None = None) -> None:
        self.errors.append(self._fmt(msg, file))
        self._emit("error", msg, file)

    def warn(self, msg: str, file: Path | str | None = None) -> None:
        self.warnings.append(self._fmt(msg, file))
        self._emit("warning", msg, file)

    def _fmt(self, msg: str, file) -> str:
        return f"{self._rel(file)}: {msg}" if file else msg

    def _rel(self, file) -> str:
        p = Path(file)
        try:
            return str(p.resolve().relative_to(ROOT))
        except ValueError:
            return str(p)

    def _emit(self, level: str, msg: str, file) -> None:
        if self.in_actions:
            loc = f" file={self._rel(file)}" if file else ""
            print(f"::{level}{loc}::{msg}")
        else:
            print(f"[{level.upper()}] {self._fmt(msg, file)}")

    def finish(self) -> int:
        print(f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)
