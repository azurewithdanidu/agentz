#!/usr/bin/env python3
"""The marketplace publishing gate. Runs every hard check a plugin must pass.

Usage:
  python3 scripts/validate_repo.py                      # all structural checks
  python3 scripts/validate_repo.py --base origin/main   # also version-bump and duplicate checks for a PR

Hard checks fail the build. The duplicate check only warns: a person (and Copilot review)
decides whether an overlap is a real duplicate.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from marketplace_lib import (
    AP_MCP_SCHEMA,
    AP_MCP_TYPES,
    AP_PLUGIN_FIELDS,
    AP_PLUGIN_SCHEMA,
    CATEGORIES,
    CLAUDE_MARKETPLACE,
    CODEOWNERS,
    COPILOT_NS,
    COPILOT_TO_CLAUDE_TOOLS,
    NAME_RE,
    ROOT,
    SEMVER_RE,
    Reporter,
    load_json,
    read_frontmatter,
    semver_tuple,
)

MIN_EVALS = 10
DESC_MIN, DESC_MAX = 50, 1024
DUPLICATE_THRESHOLD = 0.6
LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Azure storage key": re.compile(r"AccountKey=[A-Za-z0-9+/=]{40,}"),
    "connection string password": re.compile(r"(?i)password\s*=\s*[^;\s\"']{8,}"),
}
STOPWORDS = set(
    "a an and are as at be by do does for from how if in into is it its of on or that the this to "
    "use used uses using when with without you your not any all can should user users ask asks".split()
)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


# ---------------------------------------------------------------- marketplace

def check_marketplace(r: Reporter) -> dict:
    try:
        market = load_json(CLAUDE_MARKETPLACE)
    except (OSError, json.JSONDecodeError) as exc:
        r.error(f"cannot parse marketplace.json: {exc}", CLAUDE_MARKETPLACE)
        return {"plugins": []}

    for field in ("name", "owner", "plugins"):
        if field not in market:
            r.error(f"missing required field '{field}'", CLAUDE_MARKETPLACE)
    if not market.get("owner", {}).get("name"):
        r.error("owner.name is required", CLAUDE_MARKETPLACE)

    seen: set[str] = set()
    for i, entry in enumerate(market.get("plugins", [])):
        name, source = entry.get("name", ""), entry.get("source", "")
        where = f"plugins[{i}] ({name or '?'})"
        if not NAME_RE.match(name):
            r.error(f"{where}: name must be lowercase-hyphenated, max 64 chars", CLAUDE_MARKETPLACE)
        if name in seen:
            r.error(f"{where}: duplicate plugin name", CLAUDE_MARKETPLACE)
        seen.add(name)
        if not isinstance(source, str) or not source.startswith("./plugins/") or ".." in source:
            r.error(f"{where}: source must be a relative path like ./plugins/{name}", CLAUDE_MARKETPLACE)
        elif source != f"./plugins/{name}":
            r.error(f"{where}: directory name must equal plugin name (./plugins/{name})", CLAUDE_MARKETPLACE)
        if entry.get("category") not in CATEGORIES:
            r.error(f"{where}: category must be one of {sorted(CATEGORIES)}", CLAUDE_MARKETPLACE)
        if not entry.get("description"):
            r.error(f"{where}: description is required", CLAUDE_MARKETPLACE)

    registered = {e.get("name") for e in market.get("plugins", [])}
    for d in sorted((ROOT / "plugins").iterdir()):
        if d.is_dir() and d.name not in registered:
            r.error("plugin folder is not registered in .claude-plugin/marketplace.json", d)
    return market


# ---------------------------------------------------------------- per plugin

def check_plugin(r: Reporter, entry: dict, codeowners: str) -> None:
    name = entry["name"]
    pdir = ROOT / "plugins" / name
    if not pdir.is_dir():
        r.error(f"registered plugin '{name}' has no folder", CLAUDE_MARKETPLACE)
        return

    # Agent Plugins 1.0 manifest (the source of truth)
    manifest_path = pdir / "plugin.json"
    try:
        manifest = load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        r.error(f"missing or invalid Agent Plugins manifest plugin.json: {exc}", manifest_path)
        manifest = {}
    if manifest.get("$schema") != AP_PLUGIN_SCHEMA:
        r.error(f"$schema must be {AP_PLUGIN_SCHEMA}", manifest_path)
    for field in sorted(set(manifest) - AP_PLUGIN_FIELDS):
        r.error(f"'{field}' is not an Agent Plugins 1.0 field (the manifest schema is closed)", manifest_path)
    if manifest.get("name") != name:
        r.error("plugin.json name must match the folder name", manifest_path)
    if not SEMVER_RE.match(str(manifest.get("version", ""))):
        r.error("version must be semver (e.g. 0.1.0)", manifest_path)
    if not manifest.get("description"):
        r.error("description is required", manifest_path)
    author = manifest.get("author", {})
    if not isinstance(author, dict) or not author.get("name") or not author.get("email"):
        r.error("author must be an object with name and email", manifest_path)
    elif set(author) - {"name", "email", "url"}:
        r.error("author may only contain name, email and url", manifest_path)
    if "extensions" in manifest and not isinstance(manifest["extensions"], dict):
        r.error("extensions must be an object keyed by namespace", manifest_path)
    if "version" in entry:
        r.warn("set version in plugin.json only; the marketplace entry copy is ignored", CLAUDE_MARKETPLACE)

    check_mcp(r, pdir)

    # Required files and forbidden layout
    if not (pdir / "README.md").exists():
        r.error("README.md is required", pdir)
    if (pdir / "bin").is_dir():
        r.error("top-level bin/ is not allowed (Claude org sync rejects it). Use scripts/", pdir / "bin")
    if (pdir / "hooks.json").exists():
        r.error(f"hooks belong in {COPILOT_NS}/hooks/hooks.json, not at the plugin root", pdir / "hooks.json")
    if (pdir / ".plugin").exists():
        r.error("legacy OpenPlugin .plugin/ folder is not used here; plugin.json lives at the plugin root", pdir / ".plugin")

    # Ownership
    if f"/plugins/{name}/" not in codeowners:
        r.error(f"no CODEOWNERS entry for /plugins/{name}/", CODEOWNERS)

    # Skills
    skill_dirs = sorted(p for p in (pdir / "skills").glob("*") if p.is_dir()) if (pdir / "skills").is_dir() else []
    if not skill_dirs:
        r.error("at least one skill is required (skills/<name>/SKILL.md)", pdir)
    for sdir in skill_dirs:
        check_skill(r, sdir)

    # Client-specific components live in the Copilot namespace. agents/ and commands/ are generated.
    ns = pdir / COPILOT_NS
    for f in sorted((ns / "agents").glob("*")) if (ns / "agents").is_dir() else []:
        if not f.name.endswith(".agent.md"):
            r.error("agent files must be named <name>.agent.md", f)
            continue
        fm = read_frontmatter(f)
        if not fm or not fm.get("name") or not fm.get("description"):
            r.error("agent frontmatter needs name and description", f)
            continue
        if fm["name"] != f.name.removesuffix(".agent.md"):
            r.error("agent name must match the file name", f)
        tools = fm.get("tools") or []
        tools = [t.strip() for t in tools.split(",")] if isinstance(tools, str) else tools
        unknown = [t for t in tools if t not in COPILOT_TO_CLAUDE_TOOLS]
        if unknown:
            r.error(f"tools {unknown} have no Claude mapping; use {sorted(COPILOT_TO_CLAUDE_TOOLS)} "
                    "or extend COPILOT_TO_CLAUDE_TOOLS", f)
    for f in sorted((ns / "commands").glob("*.md")) if (ns / "commands").is_dir() else []:
        fm = read_frontmatter(f)
        if not fm or not fm.get("description"):
            r.error("command frontmatter needs a description", f)

    # Evals
    check_evals(r, pdir)

    # Secrets
    for f in pdir.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".ps1", ".bicep", ".bicepparam", ".txt"}:
            text = f.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    r.error(f"possible {label} committed", f)


def check_mcp(r: Reporter, pdir: Path) -> None:
    mcp = pdir / "mcp.json"
    if not mcp.exists():
        return
    try:
        data = load_json(mcp)
    except json.JSONDecodeError as exc:
        r.error(f"invalid JSON: {exc}", mcp)
        return
    if data.get("$schema") != AP_MCP_SCHEMA:
        r.error(f"$schema must be {AP_MCP_SCHEMA}", mcp)
    for field in sorted(set(data) - {"$schema", "mcpServers"}):
        r.error(f"unexpected top-level field '{field}'", mcp)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        r.error("mcpServers must be a non-empty object", mcp)
        return
    for name, server in servers.items():
        kind = server.get("type")
        if kind not in AP_MCP_TYPES:
            r.error(f"server '{name}': type must be one of {sorted(AP_MCP_TYPES)}", mcp)
        elif kind == "stdio" and not server.get("command"):
            r.error(f"server '{name}': stdio servers need a command", mcp)
        elif kind != "stdio" and not server.get("url"):
            r.error(f"server '{name}': {kind} servers need a url", mcp)
        if kind == "sse":
            r.warn(f"server '{name}': sse is deprecated; use streamable-http", mcp)


def check_skill(r: Reporter, sdir: Path) -> None:
    skill_md = sdir / "SKILL.md"
    if not skill_md.exists():
        r.error("skill folder has no SKILL.md", sdir)
        return
    fm = read_frontmatter(skill_md)
    if not fm:
        r.error("SKILL.md needs YAML frontmatter with name and description", skill_md)
        return
    if fm.get("name") != sdir.name:
        r.error(f"frontmatter name '{fm.get('name')}' must match folder '{sdir.name}'", skill_md)
    if not NAME_RE.match(str(fm.get("name", ""))):
        r.error("skill name must be lowercase-hyphenated, max 64 chars", skill_md)
    desc = str(fm.get("description", ""))
    if not DESC_MIN <= len(desc) <= DESC_MAX:
        r.error(f"description must be {DESC_MIN}-{DESC_MAX} chars (is {len(desc)}); it drives triggering", skill_md)
    if "use when" not in desc.lower():
        r.warn("description should say when to use the skill ('Use when ...')", skill_md)
    if "not use" not in desc.lower() and "don't use" not in desc.lower():
        r.warn("description should say when not to use the skill", skill_md)

    # Every relative link in the skill must resolve.
    for md in sorted(sdir.rglob("*.md")):
        for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
            if not (md.parent / target.split("#")[0]).exists():
                r.error(f"broken relative link: {target}", md)


def check_evals(r: Reporter, pdir: Path) -> None:
    """Evals are Vally specs (https://www.npmjs.com/package/@microsoft/vally-cli).

    CI also runs `vally lint` for schema checks; this enforces the agentz minimums.
    """
    spec = pdir / "evals" / "eval.yaml"
    if (pdir / "evals" / "evals.yaml").exists():
        r.error("evals/evals.yaml is the old placeholder format; move the cases to Vally evals/eval.yaml", pdir / "evals" / "evals.yaml")
    if not spec.exists():
        r.error(f"evals/eval.yaml (Vally format) is required, with at least {MIN_EVALS} stimuli", pdir)
        return
    try:
        data = yaml.safe_load(spec.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        r.error(f"invalid YAML: {exc}", spec)
        return

    stimuli = [s for s in (data.get("stimuli") or []) if isinstance(s, dict)]
    if len(stimuli) < MIN_EVALS:
        r.error(f"{len(stimuli)} eval stimuli; at least {MIN_EVALS} are required", spec)
    names = [s.get("name") for s in stimuli]
    if None in names or len(names) != len(set(names)):
        r.error("every stimulus needs a unique name", spec)

    triggered: set[str] = set()
    positive = negative = 0
    for s in stimuli:
        label = s.get("name", "?")
        if not (s.get("prompt") or s.get("turns")):
            r.error(f"stimulus '{label}' has no prompt (the input)", spec)
        graders = [g for g in (s.get("graders") or []) if isinstance(g, dict)]
        if not graders:
            r.error(f"stimulus '{label}' has no graders (the expected result)", spec)
        for g in graders:
            if g.get("type") != "skill-invocation":
                continue
            cfg = g.get("config") or {}
            if cfg.get("required"):
                positive += 1
                triggered.update(cfg["required"])
            if cfg.get("disallowed"):
                negative += 1
        if (s.get("tags") or {}).get("advisory") is True:
            r.warn(f"stimulus '{label}' is tagged advisory; review it and remove the tag so it counts", spec)

    if positive < 3:
        r.error(f"{positive} should-trigger case(s); at least 3 skill-invocation 'required' cases are needed", spec)
    if negative < 2:
        r.error(f"{negative} should-not-trigger case(s); at least 2 skill-invocation 'disallowed' cases are needed", spec)
    skills = {d.name for d in (pdir / "skills").iterdir() if (d / "SKILL.md").exists()} if (pdir / "skills").is_dir() else set()
    for missing in sorted(skills - triggered):
        r.error(f"skill '{missing}' has no should-trigger eval", spec)

    env = data.get("agent_environment") or {}
    for skill_path in env.get("skills") or []:
        if not (spec.parent / skill_path / "SKILL.md").exists():
            r.error(f"agent_environment.skills entry '{skill_path}' has no SKILL.md", spec)
    for f in env.get("files") or []:
        src = f.get("src") if isinstance(f, dict) else None
        if not src or not (spec.parent / src).exists():
            r.error(f"agent_environment.files src '{src}' does not exist", spec)


# ---------------------------------------------------------------- PR-only checks

def base_file(base: str, rel: str) -> str | None:
    res = run(["git", "show", f"{base}:{rel}"])
    return res.stdout if res.returncode == 0 else None


def check_version_bumps(r: Reporter, base: str, market: dict) -> None:
    diff = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    if diff.returncode != 0:
        r.error(f"cannot diff against {base}: {diff.stderr.strip()}")
        return
    changed = diff.stdout.split()
    for entry in market.get("plugins", []):
        name = entry["name"]
        prefix = f"plugins/{name}/"
        generated_prefixes = tuple(f"{prefix}{g}" for g in
                                   (".claude-plugin/", ".cursor-plugin/", ".mcp.json", "agents/", "commands/"))
        if not any(f.startswith(prefix) and not f.startswith(generated_prefixes) for f in changed):
            continue
        # Base may predate the Agent Plugins layout, so fall back to the old Claude manifest.
        old_raw = base_file(base, f"{prefix}plugin.json") or base_file(base, f"{prefix}.claude-plugin/plugin.json")
        if old_raw is None:
            continue  # new plugin
        try:
            old_v = json.loads(old_raw)["version"]
            new_v = load_json(ROOT / prefix / "plugin.json")["version"]
            if semver_tuple(new_v) <= semver_tuple(old_v):
                r.error(f"plugin changed but version was not bumped ({old_v} -> {new_v})",
                        ROOT / prefix / "plugin.json")
        except (KeyError, ValueError, json.JSONDecodeError):
            r.error("cannot compare versions with base", ROOT / prefix)


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 2}


def check_duplicates(r: Reporter, base: str) -> None:
    raw = base_file(base, "catalog.json")
    if raw is None:
        return
    old = json.loads(raw)
    new = load_json(ROOT / "catalog.json")

    def items(cat: dict) -> dict[str, tuple[str, str]]:
        out = {}
        for p in cat["plugins"]:
            for kind in ("skills", "agents"):
                for item in p[kind]:
                    out[f"{p['name']}/{kind[:-1]}/{item['name']}"] = (item["name"], item["description"])
        return out

    old_items, new_items = items(old), items(new)
    # A plugin renamed through the marketplace "renames" map is not a duplicate of its old self.
    renames = load_json(CLAUDE_MARKETPLACE).get("renames") or {}
    for key, (name, desc) in new_items.items():
        if key in old_items:
            continue
        new_tokens = tokens(name.replace("-", " ") + " " + desc)
        for okey, (oname, odesc) in old_items.items():
            old_plugin, new_plugin = okey.split("/")[0], key.split("/")[0]
            if old_plugin == new_plugin or renames.get(old_plugin) == new_plugin:
                continue
            old_tokens = tokens(oname.replace("-", " ") + " " + odesc)
            # Overlap coefficient: a short new description that is mostly contained
            # in an existing one scores high, which Jaccard would under-report.
            score = len(new_tokens & old_tokens) / max(1, min(len(new_tokens), len(old_tokens)))
            if score >= DUPLICATE_THRESHOLD:
                r.warn(f"possible duplicate: new '{key}' overlaps existing '{okey}' "
                       f"(similarity {score:.2f}). Consider reusing or extending it.", ROOT / "catalog.json")


# ---------------------------------------------------------------- main

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", help="git ref to compare against for PR checks, e.g. origin/main")
    args = parser.parse_args()

    r = Reporter()
    market = check_marketplace(r)
    codeowners = CODEOWNERS.read_text(encoding="utf-8") if CODEOWNERS.exists() else ""
    if not codeowners:
        r.error(".github/CODEOWNERS is required", CODEOWNERS)
    for entry in market.get("plugins", []):
        if entry.get("name"):
            check_plugin(r, entry, codeowners)

    for script in ("sync_manifests.py", "build_catalog.py"):
        res = run([sys.executable, f"scripts/{script}", "--check"])
        if res.returncode != 0:
            r.error(f"{script} --check failed: {res.stdout.strip()}")

    if args.base:
        check_version_bumps(r, args.base, market)
        check_duplicates(r, args.base)

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
