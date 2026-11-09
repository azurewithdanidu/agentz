# onboarding

Sets up a machine to contribute plugins to the agentz marketplace: installs agentz-publisher, HVE Core, Python with PyYAML and Vally for the evals.

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

See [what each role installs](skills/setup-machine/references/what-it-installs.md).
