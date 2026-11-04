# onboarding

Sets up a machine for the agentz marketplace: adds it to every installed client, installs the plugins you choose, and prepares contributors with Python, Vally and HVE Core.

| | |
| --- | --- |
| **Owner** | Danidu Weerasinghe (`@azurewithdanidu`) |
| **Status** | Beta (`0.x`) |
| **Format** | Agent Plugins 1.0 (Claude Code and Cursor files generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |

## Install

Add the marketplace once, then install this plugin.

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

Run `/init` and answer two questions: are you a user or a contributor, and which plugins do you want. It shows a dry run first, then does the setup and tells you what is left to do by hand.

In Claude Code the command may appear as `/onboarding:init`, because `/init` is also a built-in command there. The skill also starts when you ask to get started with agentz.

The script behind it works without the plugin:

```bash
bash skills/setup-machine/scripts/setup.sh --role contributor --dry-run
```

```powershell
.\skills\setup-machine\scripts\setup.ps1 -Role contributor -DryRun
```

See [what each role installs](skills/setup-machine/references/what-it-installs.md).
