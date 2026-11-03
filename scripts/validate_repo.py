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
    CATEGORIES,
    CLAUDE_MARKETPLACE,
    CODEOWNERS,
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

    # Manifest
    manifest_path = pdir / ".claude-plugin" / "plugin.json"
    try:
        manifest = load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        r.error(f"missing or invalid plugin.json: {exc}", manifest_path)
        manifest = {}
    if manifest.get("name") != name:
        r.error("plugin.json name must match the folder name", manifest_path)
    if not SEMVER_RE.match(str(manifest.get("version", ""))):
        r.error("version must be semver (e.g. 0.1.0)", manifest_path)
    if not manifest.get("description"):
        r.error("description is required", manifest_path)
    author = manifest.get("author", {})
    if not author.get("name") or not author.get("email"):
        r.error("author.name and author.email are required", manifest_path)
    if "version" in entry:
        r.warn("set version in plugin.json only; the marketplace entry copy is ignored", CLAUDE_MARKETPLACE)

    # Required files and forbidden layout
    if not (pdir / "README.md").exists():
        r.error("README.md is required", pdir)
    if (pdir / "bin").is_dir():
        r.error("top-level bin/ is not allowed (Claude org sync rejects it). Use scripts/", pdir / "bin")
    if (pdir / "hooks.json").exists():
        r.error("hooks belong in hooks/hooks.json, not hooks.json at the plugin root", pdir / "hooks.json")

    # Ownership
    if f"/plugins/{name}/" not in codeowners:
        r.error(f"no CODEOWNERS entry for /plugins/{name}/", CODEOWNERS)

    # Skills
    skill_dirs = sorted(p for p in (pdir / "skills").glob("*") if p.is_dir()) if (pdir / "skills").is_dir() else []
    if not skill_dirs:
        r.error("at least one skill is required (skills/<name>/SKILL.md)", pdir)
    for sdir in skill_dirs:
        check_skill(r, sdir)

    # Agents and commands
    for agent in sorted(pdir.glob("agents/*.md")):
        fm = read_frontmatter(agent)
        if not fm or not fm.get("name") or not fm.get("description"):
            r.error("agent frontmatter needs name and description", agent)
    for cmd in sorted(pdir.glob("commands/*.md")):
        fm = read_frontmatter(cmd)
        if not fm or not fm.get("description"):
            r.error("command frontmatter needs a description", cmd)

    # Evals
    check_evals(r, pdir)

    # Secrets
    for f in pdir.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".ps1", ".bicep", ".bicepparam", ".txt"}:
            text = f.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    r.error(f"possible {label} committed", f)


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
    evals = pdir / "evals" / "evals.yaml"
    if not evals.exists():
        r.error(f"evals/evals.yaml is required (minimum {MIN_EVALS} cases)", pdir)
        return
    try:
        data = yaml.safe_load(evals.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        r.error(f"invalid YAML: {exc}", evals)
        return
    cases = data.get("cases") or []
    ids = [c.get("id") for c in cases if isinstance(c, dict)]
    if len(cases) < MIN_EVALS:
        r.error(f"{len(cases)} eval case(s); at least {MIN_EVALS} are required", evals)
    if len(ids) != len(set(ids)) or None in ids:
        r.error("every eval case needs a unique id", evals)
    types = {c.get("type") for c in cases if isinstance(c, dict)}
    if "trigger" not in types:
        r.error("include trigger evals (does the skill fire on the right prompts?)", evals)


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
        generated = {f"{prefix}.cursor-plugin/plugin.json", f"{prefix}mcp.json"}
        if not any(f.startswith(prefix) and f not in generated for f in changed):
            continue
        old_raw = base_file(base, f"{prefix}.claude-plugin/plugin.json")
        if old_raw is None:
            continue  # new plugin
        try:
            old_v = json.loads(old_raw)["version"]
            new_v = load_json(ROOT / prefix / ".claude-plugin" / "plugin.json")["version"]
            if semver_tuple(new_v) <= semver_tuple(old_v):
                r.error(f"plugin changed but version was not bumped ({old_v} -> {new_v})",
                        ROOT / prefix / ".claude-plugin" / "plugin.json")
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
    for key, (name, desc) in new_items.items():
        if key in old_items:
            continue
        new_tokens = tokens(name.replace("-", " ") + " " + desc)
        for okey, (oname, odesc) in old_items.items():
            if okey.split("/")[0] == key.split("/")[0]:
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
