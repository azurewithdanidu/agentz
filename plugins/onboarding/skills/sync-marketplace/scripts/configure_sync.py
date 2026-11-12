#!/usr/bin/env python3
"""Add the agentz-sync workflow to a source repo that already uses the plugin layout.

The workflow copies the plugin's plugin.json and README.md into the agentz marketplace and opens
a draft pull request whenever the plugin version changes on the default branch. Nothing else in
the source repo changes.

Usage:
  python configure_sync.py --source . --category development --owner-handle @me           # preview
  python configure_sync.py --source . --category development --owner-handle @me --apply   # write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
REPOSITORY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]{1,100}$")
HANDLE = re.compile(r"^@[A-Za-z0-9-]+(?:/[A-Za-z0-9_.-]+)?$")
EMAIL = re.compile(r"^[^\s@\"'$`\\]+@[^\s@\"'$`\\]+\.[^\s@\"'$`\\]+$")
BRANCH = re.compile(r"^[A-Za-z0-9._/-]{1,100}$")
PLUGIN_PATH = re.compile(r"^[A-Za-z0-9._/-]{1,200}$")
CATEGORIES = ("productivity", "development", "security", "observability")
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "agentz-sync.yml"
WORKFLOW = Path(".github") / "workflows" / "agentz-sync.yml"


def find_manifest(pdir: Path) -> Path:
    for rel in ("plugin.json", ".claude-plugin/plugin.json"):
        if (pdir / rel).is_file():
            return pdir / rel
    raise ValueError("No plugin.json or .claude-plugin/plugin.json found. The sync publishes repos that "
                     "already use the plugin layout; create the plugin first.")


def normalise_path(raw: str) -> str:
    path = raw.strip().strip("/").removeprefix("./") or "."
    if path != "." and (not PLUGIN_PATH.fullmatch(path) or any(p in ("", ".", "..") for p in path.split("/"))):
        raise ValueError(f"Plugin path must be a relative folder inside the repo: {raw}")
    return path


def prepare(args: argparse.Namespace) -> tuple[Path, str, dict]:
    root = args.source.resolve(strict=True)
    if not (root / ".git").exists():
        raise ValueError("Source must be the root of a Git repository.")
    if not REPOSITORY.fullmatch(args.marketplace_repository):
        raise ValueError("Marketplace repository must be owner/repository.")
    if not BRANCH.fullmatch(args.base_branch) or ".." in args.base_branch:
        raise ValueError("Base branch is not a valid branch name.")
    if not HANDLE.fullmatch(args.owner_handle):
        raise ValueError("Owner handle must be a GitHub @user or @org/team.")
    if args.owner_email and not EMAIL.fullmatch(args.owner_email):
        raise ValueError("Owner email is not a valid email address.")

    plugin_path = normalise_path(args.plugin_path)
    pdir = (root / plugin_path).resolve()
    if not pdir.is_relative_to(root) or not pdir.is_dir():
        raise ValueError(f"Plugin path does not exist inside the source repository: {args.plugin_path}")
    manifest_path = find_manifest(pdir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not NAME.fullmatch(str(manifest.get("name", ""))):
        raise ValueError(f"{manifest_path.relative_to(root)}: name must be lowercase-hyphenated, max 64 chars.")
    if not SEMVER.fullmatch(str(manifest.get("version", ""))):
        raise ValueError(f"{manifest_path.relative_to(root)}: version must be semver, for example 1.0.0.")
    if not (pdir / "README.md").is_file():
        raise ValueError(f"No README.md in '{plugin_path}'; the marketplace copies it.")
    author = manifest.get("author")
    if not (isinstance(author, dict) and author.get("email")) and not args.owner_email:
        raise ValueError("plugin.json has no author email; pass --owner-email so the marketplace copy has one.")

    prefix = "" if plugin_path == "." else f"{plugin_path}/"
    values = {
        "__MARKETPLACE_REPOSITORY__": args.marketplace_repository,
        "__BASE_BRANCH__": args.base_branch,
        "__PLUGIN_PATH__": plugin_path,
        "__PLUGIN_PATH_PREFIX__": prefix,
        "__CATEGORY__": args.category,
        "__OWNER_HANDLE__": args.owner_handle,
        "__OWNER_EMAIL__": args.owner_email or "",
    }
    content = TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace(key, value)

    target = root / WORKFLOW
    for parent in (target, *target.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f"Workflow destination must not use a symbolic link: {parent}")
    return target, content, manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=Path.cwd(), help="root of the source repo")
    parser.add_argument("--plugin-path", default=".", help="plugin folder inside the repo (default: root)")
    parser.add_argument("--category", choices=CATEGORIES, required=True)
    parser.add_argument("--owner-handle", required=True, help="GitHub @user or @org/team for CODEOWNERS")
    parser.add_argument("--owner-email", help="author email, used only if plugin.json has none")
    parser.add_argument("--marketplace-repository", default="azurewithdanidu/agentz")
    parser.add_argument("--base-branch", default="main", help="marketplace branch to target")
    parser.add_argument("--apply", action="store_true", help="write the workflow (default: preview)")
    parser.add_argument("--force", action="store_true", help="replace an existing, different agentz-sync.yml")
    args = parser.parse_args(argv)
    try:
        target, content, manifest = prepare(args)
        if target.exists() and target.read_text(encoding="utf-8") != content and not args.force:
            raise ValueError(f"{WORKFLOW.as_posix()} already exists with different content; "
                             "review it, then re-run with --force to replace it.")
        print(f"Plugin: {manifest['name']} {manifest['version']}")
        if not args.apply:
            print(f"--- {WORKFLOW.as_posix()} (preview) ---\n{content}", end="")
            print("Preview only. Re-run with --apply to write the workflow.")
            return 0
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Wrote {WORKFLOW.as_posix()}. Next: add the AGENTZ_MARKETPLACE_TOKEN secret, commit the "
              "workflow, then bump the plugin version to publish.")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
