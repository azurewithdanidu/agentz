---
name: sync-marketplace
description: Add a GitHub Actions workflow to a source repo that already contains a plugin, so each new plugin version is published to the agentz marketplace as a linked plugin through a draft pull request. Use when someone asks to sync, publish or keep a plugin from their own repo up to date in the marketplace. Do not use for ordinary machine setup, installing plugins, building a new plugin from loose artifacts, or reviewing a pull request.
---

# Sync a plugin repo to the marketplace

Set up the `agentz-sync` workflow in a source repo. When the plugin version changes on the default branch, the workflow copies `plugin.json` and `README.md` into `plugins/<name>/` in the marketplace, pins the registry entry to that commit, and opens or updates a draft pull request. The skills, agents and commands stay in the source repo, and clients install them from the pinned commit.

## When to use

Use when the repo already has a plugin layout: `plugin.json` or `.claude-plugin/plugin.json` with `skills/`, and optionally `agents/` and `commands/`, plus a `README.md`.

## When not to use

- If the repo has loose artifacts and no plugin manifest, point the user to `agentz-publisher` (`/new-plugin`) to build the plugin first.
- For contributor machine setup, use `setup-machine`.
- Don't use this skill to install plugins or review pull requests.

## Inputs

Collect these inputs:

- The source repo root.
- The plugin folder, if the plugin is not at the repo root.
- The marketplace category: productivity, development, security or observability.
- The GitHub `@user` or `@org/team` that owns the plugin.
- An author email, if `plugin.json` has none.
- The marketplace repo, if it is not `azurewithdanidu/agentz`.

Never ask the user to paste a token into chat.

## Workflow

1. Read [setup and safety](references/setup.md).
2. Confirm the source repo is the one the user intends to publish. If the repo is private, warn the user that the marketplace PR makes `plugin.json` and `README.md` public. Also warn that public marketplace CI can't fetch a private source, so the gate fails.
3. Run `scripts/configure_sync.py` relative to this skill, without `--apply`, and show the user the preview.
4. After the user approves, re-run the script with `--apply`. It writes only `.github/workflows/agentz-sync.yml`. Pass `--force` only if the user asks to replace an existing workflow.
5. Tell the user how to finish setup:
   1. Add the `AGENTZ_MARKETPLACE_TOKEN` secret.
   2. Commit the workflow.
   3. Bump the plugin version, which publishes the plugin.

## Safety and stop conditions

- Don't create, move or edit plugin files in the source repo. The workflow file is the only change.
- Stop if the repo has no plugin manifest or README, if the name or version is invalid, or if a different workflow already exists and the user hasn't asked to replace it.
- Never push, merge or approve the marketplace pull request yourself. The workflow opens the pull request as a draft for owner review.

## Outputs

Report the following:

- The plugin name and version.
- The workflow path.
- Whether the workflow file was written or only previewed.
- The remaining steps: the secret, the commit and the version bump.
