---
description: How the agentz-sync workflow publishes a linked plugin, and what the source repo owner must set up.
---

# Source repo setup

## What gets published

The marketplace gets a *linked plugin*, made up of three parts:

- `plugins/<name>/plugin.json`: a copy of the source manifest, reduced to the fields the marketplace accepts. If the source manifest has no author email, the one passed to `/init` is used.
- `plugins/<name>/README.md`: a copy of the source README.
- A registry entry whose `source` points to the source repo at a pinned commit:

```json
{ "source": "github", "repo": "owner/repo", "sha": "<40-character commit>", "path": "<plugin folder, if not the root>" }
```

Clients install skills, agents and commands from that commit. The marketplace CI fetches the same commit and runs the usual plugin checks on it: skill structure, agents without `tools`, Vally evals, MCP config and secrets. A problem has to be fixed in the source repo, so the PR goes through the same gate as any other plugin.

## When the workflow runs

- The workflow runs on pushes to the default branch that change `plugin.json`, `.claude-plugin/plugin.json` or the workflow itself. You can also start it manually.
- It publishes only when the source version is higher than the marketplace copy. Otherwise it exits with a notice asking you to bump the version: clients read the version from the pinned commit, so the marketplace can't bump it for you.
- It pushes the branch `agentz-sync/<name>` in the marketplace and opens a draft pull request. Later runs replace that branch and update the same pull request.

## Run the setup script

Run it from the installed `sync-marketplace` skill:

```text
python <installed-skill>/scripts/configure_sync.py --source <repo-root> \
  --category development --owner-handle @<user-or-team> [--owner-email <email>] \
  [--plugin-path <folder>] [--marketplace-repository <owner/repo>] [--base-branch main]
```

The script previews the workflow by default. Add `--apply` to write `.github/workflows/agentz-sync.yml`. It won't replace a different existing workflow unless you pass `--force`.

## Secret

Add one GitHub Actions secret to the source repo:

- `AGENTZ_MARKETPLACE_TOKEN`: a fine-grained personal access token, or a GitHub App token, for the marketplace repo with **Contents** and **Pull requests** set to read and write.
  - The default `GITHUB_TOKEN` can't write to another repo.
  - PRs opened with this token trigger the marketplace checks.

Never paste the token into chat or commit it to a file.

## Limits

- **Private sources:** the marketplace PR makes `plugin.json` and `README.md` public. Public marketplace CI can't fetch a private source, so the gate reports a fetch error. Use a marketplace the source is visible to.
- **Client support:** remote `github` sources are documented for Claude Code and Copilot CLI. VS Code and Cursor support for them is not yet verified.
- **Duplicate checks:** the marketplace duplicate check doesn't yet compare the skills inside linked plugins. Reviewers check reuse by hand.
- **Workflow source:** the workflow runs the sync script from the marketplace's base branch, so it always uses the marketplace's current rules.
