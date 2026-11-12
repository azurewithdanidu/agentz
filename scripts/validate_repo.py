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
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from marketplace_lib import (
    AP_SCHEMA_HOST,
    CATEGORIES,
    CLAUDE_MARKETPLACE,
    CODEOWNERS,
    COMMIT_SHA_RE,
    COPILOT_NS,
    GITHUB_REPO_RE,
    LINKED_FILES,
    MCP_TYPES,
    NAME_RE,
    PLUGIN_FIELDS,
    ROOT,
    SEMVER_RE,
    Reporter,
    is_linked,
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
        if is_linked(entry):
            check_linked_source(r, where, source)
        elif not isinstance(source, str) or not source.startswith("./plugins/") or ".." in source:
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

    # Manifest (the source of truth)
    manifest_path = pdir / "plugin.json"
    try:
        manifest = load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        r.error(f"missing or invalid manifest plugin.json: {exc}", manifest_path)
        manifest = {}
    if AP_SCHEMA_HOST in str(manifest.get("$schema", "")):
        r.error("remove the Agent Plugins $schema: it switches Copilot to Agent Plugins rules, which ignore "
                "the root agents/ folder", manifest_path)
    if "extensions" in manifest:
        r.error("remove 'extensions': it belongs to the Agent Plugins format, not the classic layout", manifest_path)
    for field in sorted(set(manifest) - PLUGIN_FIELDS - {"$schema", "extensions"}):
        r.error(f"'{field}' is not a supported plugin.json field ({', '.join(sorted(PLUGIN_FIELDS))})", manifest_path)
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
    if "version" in entry:
        r.warn("set version in plugin.json only; the marketplace entry copy is ignored", CLAUDE_MARKETPLACE)

    if not (pdir / "README.md").exists():
        r.error("README.md is required", pdir)

    # Ownership
    if f"/plugins/{name}/" not in codeowners:
        r.error(f"no CODEOWNERS entry for /plugins/{name}/", CODEOWNERS)

    if is_linked(entry):
        check_linked(r, entry, pdir, manifest)
    else:
        check_content(r, pdir)


def check_content(r, pdir: Path, scan_roots: list[Path] | None = None) -> None:
    """Checks on a plugin's components: in the marketplace, or in a linked plugin's pinned source."""
    check_mcp(r, pdir)

    if (pdir / "bin").is_dir():
        r.error("top-level bin/ is not allowed (Claude org sync rejects it). Use scripts/", pdir / "bin")
    if (pdir / COPILOT_NS).exists():
        r.error(f"{COPILOT_NS}/ is not used. Put agents in agents/<name>.agent.md and commands in commands/<name>.md "
                "so every client reads one copy", pdir / COPILOT_NS)
    if (pdir / ".plugin").exists():
        r.error("legacy OpenPlugin .plugin/ folder is not used here; plugin.json lives at the plugin root", pdir / ".plugin")

    # Skills
    skill_dirs = sorted(p for p in (pdir / "skills").glob("*") if p.is_dir()) if (pdir / "skills").is_dir() else []
    if not skill_dirs:
        r.error("at least one skill is required (skills/<name>/SKILL.md)", pdir)
    for sdir in skill_dirs:
        check_skill(r, sdir)

    # Agents and commands live at the plugin root and are read as-is by Copilot and Claude Code.
    for f in sorted((pdir / "agents").glob("*")) if (pdir / "agents").is_dir() else []:
        if not f.name.endswith(".agent.md"):
            r.error("agent files must be named <name>.agent.md", f)
            continue
        fm = read_frontmatter(f)
        if not fm or not fm.get("name") or not fm.get("description"):
            r.error("agent frontmatter needs name and description", f)
            continue
        if fm["name"] != f.name.removesuffix(".agent.md"):
            r.error("agent name must match the file name", f)
        if "tools" in fm:
            r.error("remove 'tools' from shared agents: Copilot and Claude Code use different tool names. "
                    "State limits (for example read-only) in the agent body instead", f)
    for f in sorted((pdir / "commands").glob("*.md")) if (pdir / "commands").is_dir() else []:
        fm = read_frontmatter(f)
        if not fm or not fm.get("description"):
            r.error("command frontmatter needs a description", f)

    # Evals
    check_evals(r, pdir)

    # Secrets
    files = (f for root in (scan_roots or [pdir]) for f in ([root] if root.is_file() else root.rglob("*")))
    for f in files:
        if f.is_file() and f.suffix in {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".ps1", ".bicep", ".bicepparam", ".txt"}:
            text = f.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    r.error(f"possible {label} committed", f)


# ---------------------------------------------------------------- linked plugins

# Plugin components fetched from a linked plugin's source repo (sparse checkout keeps the fetch small).
LINKED_COMPONENTS = ("plugin.json", ".claude-plugin/", "skills/", "agents/", "commands/", "evals/",
                     ".mcp.json", "bin/", f"{COPILOT_NS}/", ".plugin/")


def check_linked_source(r: Reporter, where: str, source: dict) -> None:
    if set(source) - {"source", "repo", "sha", "path"}:
        r.error(f"{where}: linked source may only contain source, repo, sha and path", CLAUDE_MARKETPLACE)
    if source.get("source") != "github":
        r.error(f"{where}: linked source must be {{\"source\": \"github\", ...}}", CLAUDE_MARKETPLACE)
    if not GITHUB_REPO_RE.match(str(source.get("repo", ""))):
        r.error(f"{where}: linked source repo must be owner/repo", CLAUDE_MARKETPLACE)
    if not COMMIT_SHA_RE.match(str(source.get("sha", ""))):
        r.error(f"{where}: linked source must pin a full 40-character lowercase commit sha, so every "
                "update goes through a reviewed PR", CLAUDE_MARKETPLACE)
    path = source.get("path")
    if path is not None and (not isinstance(path, str) or not path or path.startswith("/") or "\\" in path
                             or any(p in ("", ".", "..") for p in path.rstrip("/").split("/"))):
        r.error(f"{where}: linked source path must be a relative folder without '..'", CLAUDE_MARKETPLACE)


class PrefixedReporter:
    """Reports findings in a fetched source as <repo>@<sha>/<path> instead of a temp folder."""

    def __init__(self, r: Reporter, root: Path, label: str) -> None:
        self.r, self.root, self.label = r, root, label

    def _map(self, file):
        if file is None:
            return self.label
        try:
            return f"{self.label}/{Path(file).relative_to(self.root).as_posix()}"
        except ValueError:
            return file

    def error(self, msg: str, file=None) -> None:
        self.r.error(msg, self._map(file))

    def warn(self, msg: str, file=None) -> None:
        self.r.warn(msg, self._map(file))


def fetch_linked(source: dict, dest: Path) -> str | None:
    """Sparse-fetch the plugin components at the pinned commit. Returns an error message or None."""
    prefix = source.get("path", "").strip("/")
    prefix = f"/{prefix}/" if prefix else "/"
    url = f"https://github.com/{source['repo']}.git"
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    for cmd in (
        ["git", "init", "-q", str(dest)],
        ["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", *(prefix + c for c in LINKED_COMPONENTS)],
        ["git", "-C", str(dest), "fetch", "-q", "--depth", "1", url, source["sha"]],
        ["git", "-C", str(dest), "-c", "core.longpaths=true", "checkout", "-q", "FETCH_HEAD"],
    ):
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if res.returncode:
            return res.stderr.strip() or f"{cmd[1:4]} failed"
    return None


def check_linked(r: Reporter, entry: dict, pdir: Path, manifest: dict) -> None:
    """A linked plugin keeps plugin.json and README.md here; its components are checked at the pinned commit."""
    source = entry["source"]
    for f in sorted(pdir.iterdir()):
        if f.name not in LINKED_FILES:
            r.error(f"linked plugins keep only {', '.join(sorted(LINKED_FILES))} in the marketplace; "
                    f"'{f.name}' belongs in {source.get('repo')}", f)
    if not (GITHUB_REPO_RE.match(str(source.get("repo", ""))) and COMMIT_SHA_RE.match(str(source.get("sha", "")))):
        return  # already reported by check_marketplace

    label = f"{source['repo']}@{source['sha'][:7]}"
    with tempfile.TemporaryDirectory(prefix="agentz-linked-") as tmp:
        error = fetch_linked(source, Path(tmp))
        if error:
            r.error(f"cannot fetch linked source {label}: {error}", pdir / "plugin.json")
            return
        cdir = Path(tmp) / source.get("path", "").strip("/")
        remote_path = cdir / "plugin.json"
        if not remote_path.is_file():
            remote_path = cdir / ".claude-plugin" / "plugin.json"
        try:
            remote = load_json(remote_path)
        except (OSError, json.JSONDecodeError) as exc:
            r.error(f"linked source {label} has no valid plugin.json or .claude-plugin/plugin.json: {exc}",
                    pdir / "plugin.json")
            return
        for field in ("name", "version"):
            if remote.get(field) != manifest.get(field):
                r.error(f"plugin.json {field} '{manifest.get(field)}' does not match the source at {label} "
                        f"('{remote.get(field)}'); re-run the sync workflow", pdir / "plugin.json")
        if AP_SCHEMA_HOST in str(remote.get("$schema", "")):
            r.error("remove the Agent Plugins $schema from the source plugin.json: it switches Copilot to "
                    "Agent Plugins rules", f"{label}/{remote_path.relative_to(tmp).as_posix()}")
        scan = [cdir / c.rstrip("/") for c in LINKED_COMPONENTS if (cdir / c.rstrip("/")).exists()]
        check_content(PrefixedReporter(r, Path(tmp), label), cdir, scan)


def check_mcp(r: Reporter, pdir: Path) -> None:
    mcp = pdir / ".mcp.json"
    if not mcp.exists():
        return
    try:
        data = load_json(mcp)
    except json.JSONDecodeError as exc:
        r.error(f"invalid JSON: {exc}", mcp)
        return
    for field in sorted(set(data) - {"mcpServers"}):
        r.error(f"unexpected top-level field '{field}'", mcp)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        r.error("mcpServers must be a non-empty object", mcp)
        return
    for name, server in servers.items():
        kind = server.get("type")
        if kind not in MCP_TYPES:
            r.error(f"server '{name}': type must be one of {sorted(MCP_TYPES)}", mcp)
        elif kind == "stdio" and not server.get("command"):
            r.error(f"server '{name}': stdio servers need a command", mcp)
        elif kind != "stdio" and not server.get("url"):
            r.error(f"server '{name}': {kind} servers need a url", mcp)
        if kind == "sse":
            r.warn(f"server '{name}': sse is deprecated; use http", mcp)


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
    try:
        base_sources = {e.get("name"): e.get("source") for e in
                        json.loads(base_file(base, ".claude-plugin/marketplace.json") or "{}").get("plugins", [])}
    except json.JSONDecodeError:
        base_sources = {}
    for entry in market.get("plugins", []):
        name = entry["name"]
        prefix = f"plugins/{name}/"
        generated_prefixes = tuple(f"{prefix}{g}" for g in
                                   (".claude-plugin/", ".cursor-plugin/", "mcp.json"))
        # A linked plugin changes when its pinned source changes, even if the copied files don't.
        source_moved = name in base_sources and base_sources[name] != entry.get("source")
        if not source_moved and not any(f.startswith(prefix) and not f.startswith(generated_prefixes) for f in changed):
            continue
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
