---
description: Set up marketplace contributors and source repository sync.
---

# onboarding

Sets up a machine to contribute plugins to the agentz marketplace, and sets up a plugin repo of your own to publish each new version to the marketplace through a pull request.

| | |
| --- | --- |
| **Owner** | Danidu Weerasinghe (`@azurewithdanidu`) |
| **Status** | Beta (`0.x`) |
| **Format** | Classic plugin layout (Claude Code and Cursor manifests generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code |

## Install

Add the marketplace once, then install this plugin. It is for contributors; people who only use plugins don't need it.

```text
# VS Code: add "azurewithdanidu/agentz" to chat.plugins.marketplaces, then install onboarding
# Copilot CLI
copilot plugin marketplace add azurewithdanidu/agentz
copilot plugin install onboarding@agentz
# Claude Code
/plugin marketplace add azurewithdanidu/agentz
/plugin install onboarding@agentz
```

## Usage

Run `/init` from a clone of the repository. It shows a dry run, then installs what a contributor needs and tells you what is left to do by hand.

In Claude Code the command may appear as `/onboarding:init`, because `/init` is also a built-in command there. The skill also starts when you ask to start contributing to agentz.

The script behind it works without the plugin:

```bash
bash skills/setup-machine/scripts/setup.sh --dry-run
```

```powershell
.\skills\setup-machine\scripts\setup.ps1 -DryRun
```

The `contributor-conventions` skill holds the agentz authoring and eval rules (where files go, skill and agent rules, eval minimums), so they apply in every client rather than only where `.github/instructions/` is read. It starts when you create or change plugin content or ask what the gate requires.

See [what each role installs](skills/setup-machine/references/what-it-installs.md).

### Publish a plugin from your own repo

If your plugin lives in its own repo and already uses the plugin layout (`plugin.json` or `.claude-plugin/plugin.json`, `skills/` and a `README.md`), run `/init` there. The `sync-marketplace` skill adds one file, `.github/workflows/agentz-sync.yml`, and doesn't change anything else in your repo.

When you bump the plugin version on your default branch, the workflow copies `plugin.json` and `README.md` into `plugins/<name>/` in agentz. It pins the registry entry to your commit and opens a draft pull request. Clients install the plugin's skills, agents and commands straight from that commit. The marketplace gate checks them there, so the pull request has to pass the same rules as any other plugin.

You need a single secret, `AGENTZ_MARKETPLACE_TOKEN`. In a private repo, the pull request makes `plugin.json` and `README.md` public. See [source repo setup](skills/sync-marketplace/references/setup.md) for the details and current limits.
