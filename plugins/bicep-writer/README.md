# bicep-writer

Writes new Azure Bicep templates composed from Azure Verified Modules (AVM), with pinned module versions, secure defaults and local compile checks.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Beta (`0.x`) |
| **Format** | Classic plugin layout (Claude Code and Cursor manifests generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |

## What's inside

| Component | Name | Portable across IDEs |
| --- | --- | --- |
| Skill | `bicep-writer` | Yes |

## Install

```text
/plugin install bicep-writer --marketplace azurewithdanidu/agentz
```

See [docs/consuming-plugins.md](../../docs/consuming-plugins.md) for other IDEs.

## Usage

Ask: "Write a Bicep template for a storage account using AVM modules."

The skill confirms the plan with you, maps each resource to a pinned AVM module, writes the `.bicep` and `.bicepparam` files, and compiles them locally. It never deploys, and it never writes secret values into files. For reviewing existing Bicep, use `bicep-avm-review` instead.
