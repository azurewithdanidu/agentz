#!/usr/bin/env python3
"""Publish a plugin from its source repo to the agentz marketplace as a linked plugin.

Runs in the source repo's agentz-sync workflow, from a checkout of the marketplace. It copies
only plugin.json and README.md into plugins/<name>/, pins the registry entry to the source
commit, regenerates the derived files and opens (or updates) a draft pull request. The source
repo is never changed, and the plugin's skills, agents and commands stay where they are.

A sync only happens when the source version is higher than the marketplace copy: clients read
plugin.json from the pinned commit, so the version must be bumped in the source.

Usage:
  python sync.py --source . --marketplace marketplace --source-repository owner/repo \\
      --source-sha <sha> --category development --owner-handle @me [--publish]

Without --publish this is a dry run: the marketplace checkout is updated but nothing is pushed.
Requires git, and gh with GH_TOKEN when publishing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BOT_NAME = "agentz-sync"
BOT_EMAIL = "agentz-sync@users.noreply.github.com"


class SyncError(Exception):
    pass


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and res.returncode:
        raise SyncError(f"{' '.join(cmd[:3])} failed: {(res.stderr or res.stdout).strip()}")
    return res


def load_lib(marketplace: Path):
    """Import the marketplace's own rules so the sync can never disagree with the gate."""
    scripts = marketplace / "scripts"
    if not (scripts / "marketplace_lib.py").is_file():
        raise SyncError(f"{marketplace} is not an agentz marketplace checkout (no scripts/marketplace_lib.py)")
    sys.path.insert(0, str(scripts))
    import marketplace_lib
    import validate_repo
    return marketplace_lib, validate_repo


def read_file(path: Path) -> str:
    if path.is_symlink():
        raise SyncError(f"{path.name} is a symlink; copy the real file instead")
    return path.read_text(encoding="utf-8")


def read_source(source: Path, plugin_path: str) -> tuple[dict, str, str]:
    pdir = (source / plugin_path).resolve()
    if source.resolve() not in (pdir, *pdir.parents):
        raise SyncError(f"--plugin-path '{plugin_path}' is outside the source repo")
    for rel in ("plugin.json", ".claude-plugin/plugin.json"):
        if (pdir / rel).is_file():
            manifest_rel = rel
            break
    else:
        raise SyncError(f"no plugin.json or .claude-plugin/plugin.json in '{plugin_path}'. "
                        "This sync publishes repos that already use the plugin layout")
    try:
        manifest = json.loads(read_file(pdir / manifest_rel))
    except json.JSONDecodeError as exc:
        raise SyncError(f"{manifest_rel} is not valid JSON: {exc}") from exc
    if not (pdir / "README.md").is_file():
        raise SyncError(f"no README.md in '{plugin_path}'; the marketplace needs one")
    return manifest, read_file(pdir / "README.md"), manifest_rel


def normalise_manifest(manifest: dict, lib, owner_email: str | None) -> dict:
    """Keep the fields the marketplace accepts. Values come from the source; only a missing email is filled in."""
    name, version = str(manifest.get("name", "")), str(manifest.get("version", ""))
    if not lib.NAME_RE.match(name):
        raise SyncError(f"plugin name '{name}' must be lowercase-hyphenated, max 64 chars")
    if not lib.SEMVER_RE.match(version):
        raise SyncError(f"version '{version}' must be semver (for example 1.4.0)")
    out = {k: manifest[k] for k in ("name", "version", "description", "author", "homepage",
                                    "repository", "license", "keywords")
           if k in manifest and k in lib.PLUGIN_FIELDS}
    author = out.get("author")
    if isinstance(author, str):
        author = {"name": author}
    if isinstance(author, dict):
        author = {k: v for k, v in author.items() if k in ("name", "email", "url")}
        if not author.get("email") and owner_email:
            author["email"] = owner_email
        out["author"] = author
    return out


def scan_secrets(texts: dict[str, str], patterns: dict) -> None:
    for rel, text in texts.items():
        for label, pattern in patterns.items():
            if pattern.search(text):
                raise SyncError(f"possible {label} in {rel}; nothing was published")


def same_repo(a: str, b: str) -> bool:
    return a.lower() == b.lower()


def update_marketplace(market_root: Path, lib, manifest: dict, readme: str, args) -> str | None:
    """Write the copy and the registry entry. Returns a skip reason, or None when there is something to publish."""
    name = manifest["name"]
    registry_path = market_root / ".claude-plugin" / "marketplace.json"
    registry = lib.load_json(registry_path)
    plugins = registry.setdefault("plugins", [])
    index = next((i for i, e in enumerate(plugins) if e.get("name") == name), None)
    entry = plugins[index] if index is not None else None

    if entry is not None and not lib.is_linked(entry):
        raise SyncError(f"'{name}' is already a plugin that lives in the marketplace. Rename the plugin, "
                        "or ask the marketplace owners to convert it to a linked plugin")
    if entry is not None and not same_repo(entry["source"].get("repo", ""), args.source_repository):
        raise SyncError(f"'{name}' is already linked to {entry['source'].get('repo')}. Rename the plugin")

    pdir = market_root / "plugins" / name
    if entry is not None and (pdir / "plugin.json").is_file():
        current = lib.load_json(pdir / "plugin.json").get("version", "0.0.0")
        if lib.semver_tuple(manifest["version"]) <= lib.semver_tuple(current):
            if entry["source"].get("sha") == args.source_sha:
                return f"'{name}' {current} is already published from {args.source_sha[:7]}"
            return (f"'{name}' is {manifest['version']} in the source and {current} in the marketplace. "
                    "Bump the version in plugin.json to publish this change")

    category = args.category or (entry or {}).get("category")
    if category not in lib.CATEGORIES:
        raise SyncError(f"--category must be one of {sorted(lib.CATEGORIES)}")
    source = {"source": "github", "repo": args.source_repository, "sha": args.source_sha}
    plugin_path = args.plugin_path.strip("/").removeprefix("./")
    if plugin_path and plugin_path != ".":
        source["path"] = plugin_path
    new_entry = {**(entry or {}), "name": name, "source": source,
                 "description": manifest.get("description") or (entry or {}).get("description", ""),
                 "category": category}
    if index is None:
        plugins.append(new_entry)
    else:
        plugins[index] = new_entry
    registry_path.write_text(lib.dump_json(registry), encoding="utf-8")

    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "plugin.json").write_text(lib.dump_json(manifest), encoding="utf-8")
    (pdir / "README.md").write_text(readme, encoding="utf-8")

    codeowners = market_root / ".github" / "CODEOWNERS"
    text = codeowners.read_text(encoding="utf-8") if codeowners.exists() else ""
    if f"/plugins/{name}/" not in text:
        if not args.owner_handle:
            raise SyncError("--owner-handle is required the first time a plugin is published")
        handle = args.owner_handle if args.owner_handle.startswith("@") else f"@{args.owner_handle}"
        codeowners.write_text(text.rstrip("\n") + f"\n/plugins/{name}/ {handle}\n", encoding="utf-8")
    return None


def regenerate(market_root: Path) -> None:
    for script in ("sync_manifests.py", "build_catalog.py"):
        run([sys.executable, f"scripts/{script}"], market_root)


def validate(market_root: Path, base_branch: str) -> tuple[bool, str]:
    res = run([sys.executable, "scripts/validate_repo.py", "--base", f"origin/{base_branch}"], market_root, check=False)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def pr_body(manifest: dict, args, passed: bool, report: str) -> str:
    source_url = f"https://github.com/{args.source_repository}"
    status = "passes" if passed else "fails; see the report below and fix it in the source repo"
    report = report[-6000:]
    return f"""## What this changes

Publishes `{manifest['name']}` {manifest['version']} as a linked plugin from [{args.source_repository}]({source_url}) at [`{args.source_sha[:7]}`]({source_url}/commit/{args.source_sha}).
The marketplace keeps only `plugin.json` and `README.md`; clients install the plugin from the pinned commit.

Opened by the `agentz-sync` workflow in the source repo. Fix problems in the source repo and bump its version; the workflow updates this pull request.

## Reuse check

- [ ] I searched `catalog.json` (or ran `research-catalog`) and nothing existing does this job, **or** I am extending the existing plugin: `<name>`
- [ ] Research verdict and readiness report (from `agentz-publisher`), if used: <!-- paste the summary -->

## Publishing checklist

- [x] Ran `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`
- [{'x' if passed else ' '}] `python3 scripts/validate_repo.py` passes locally ({status})
- [x] Version bumped in the plugin's root `plugin.json` (patch, minor or major)
- [ ] Vally evals in `evals/eval.yaml`: at least 10 stimuli, every skill has a should-trigger case, 2+ should-not-trigger cases
- [ ] `vally lint` passes and `vally eval` passes locally (no `advisory: true` tags left)
- [ ] Plugin README states owner, status, platforms and usage
- [ ] Tested in VS Code, plus any other client you target: <!-- Copilot CLI / Claude Code / Cursor -->

<details><summary>validate_repo.py report</summary>

```text
{report}
```

</details>
"""


def publish(market_root: Path, manifest: dict, args, body: str) -> str:
    branch = f"agentz-sync/{manifest['name']}"
    title = f"feat: publish {manifest['name']} {manifest['version']} from {args.source_repository}"
    run(["git", "checkout", "-B", branch], market_root)
    run(["git", "add", "-A"], market_root)
    run(["git", "-c", f"user.name={BOT_NAME}", "-c", f"user.email={BOT_EMAIL}", "commit", "-q", "-m", title,
         "-m", f"Source: {args.source_repository}@{args.source_sha}"], market_root)
    # The branch belongs to the bot and is fully derived from the source, so replacing it is safe.
    run(["git", "push", "--force", "origin", f"HEAD:refs/heads/{branch}"], market_root)
    body_file = market_root / ".git" / "agentz-sync-body.md"
    body_file.write_text(body, encoding="utf-8")
    existing = run(["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number",
                    "--jq", ".[0].number"], market_root).stdout.strip()
    if existing:
        run(["gh", "pr", "edit", existing, "--title", title, "--body-file", str(body_file)], market_root)
        return f"updated pull request #{existing}"
    url = run(["gh", "pr", "create", "--draft", "--base", args.base_branch, "--head", branch,
               "--title", title, "--body-file", str(body_file)], market_root).stdout.strip()
    return f"opened draft pull request {url}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=Path("."), help="source repo checkout")
    parser.add_argument("--plugin-path", default=".", help="plugin folder inside the source repo")
    parser.add_argument("--marketplace", type=Path, required=True, help="marketplace repo checkout")
    parser.add_argument("--source-repository", required=True, help="owner/repo of the source")
    parser.add_argument("--source-sha", required=True, help="full commit sha to pin")
    parser.add_argument("--category", help="marketplace category (required the first time)")
    parser.add_argument("--owner-handle", help="GitHub @handle or @org/team for CODEOWNERS (required the first time)")
    parser.add_argument("--owner-email", help="author email, used only if plugin.json has none")
    parser.add_argument("--base-branch", default="main", help="marketplace branch to target")
    parser.add_argument("--publish", action="store_true", help="push the branch and open or update the pull request")
    args = parser.parse_args(argv)

    try:
        lib, gate = load_lib(args.marketplace.resolve())
        if not lib.GITHUB_REPO_RE.match(args.source_repository):
            raise SyncError("--source-repository must be owner/repo")
        if not lib.COMMIT_SHA_RE.match(args.source_sha):
            raise SyncError("--source-sha must be a full 40-character lowercase commit sha")
        raw, readme, manifest_rel = read_source(args.source, args.plugin_path)
        manifest = normalise_manifest(raw, lib, args.owner_email)
        scan_secrets({manifest_rel: lib.dump_json(manifest), "README.md": readme}, gate.SECRET_PATTERNS)

        market_root = args.marketplace.resolve()
        skipped = update_marketplace(market_root, lib, manifest, readme, args)
        if skipped:
            print(f"::notice::{skipped}")
            return 0
        regenerate(market_root)
        if not run(["git", "status", "--porcelain"], market_root).stdout.strip():
            print(f"::notice::'{manifest['name']}' is already up to date in the marketplace")
            return 0
        passed, report = validate(market_root, args.base_branch)
        print(report)
        body = pr_body(manifest, args, passed, report)
        if not args.publish:
            print(f"Dry run: marketplace checkout updated for {manifest['name']} {manifest['version']}; "
                  "re-run with --publish to open the pull request")
            return 0
        print(publish(market_root, manifest, args, body))
        return 0
    except SyncError as exc:
        print(f"::error::{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
