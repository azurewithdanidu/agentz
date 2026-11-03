# plugin-creator

Scaffolds a new plugin that meets the marketplace standard: manifests, a first skill, an evals file, a CODEOWNERS entry and a marketplace registration. Start here when contributing.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Stable (`1.x`) |
| **Platforms** | Claude Code, VS Code (Copilot), Copilot CLI, Cursor |

## What's inside

| Component | Name | Portable across IDEs |
| --- | --- | --- |
| Skill | `create-plugin` | Yes |
| Command | `/new-plugin` | Varies by IDE |
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
