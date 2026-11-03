# plugin-creator

Scaffolds a new plugin in the open Agent Plugins 1.0 format that meets the marketplace standard: manifest, a first skill, an evals file, a CODEOWNERS entry and a marketplace registration. Start here when contributing.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Stable (`1.x`) |
| **Format** | Agent Plugins 1.0 (Claude Code and Cursor files generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |

## What's inside

| Component | Name | Portable across IDEs |
| --- | --- | --- |
| Skill | `create-plugin` | Yes |
| Command | `/new-plugin` | Copilot namespace; Claude copy generated |
| Script | `scripts/scaffold.py` | Yes (Python 3.10+) |

## Install

```text
/plugin install plugin-creator --marketplace azurewithdanidu/agentz
```

See [docs/consuming-plugins.md](../../docs/consuming-plugins.md) for other IDEs.

## Usage

```text
/new-plugin terraform-to-bicep
```

Or ask: "Create a new plugin for the marketplace."
