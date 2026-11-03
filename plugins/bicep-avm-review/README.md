# bicep-avm-review

Reviews Bicep templates against Azure Verified Modules (AVM) and organisation IaC conventions. Produces a findings report with evidence. Read-only: it never edits files or deploys.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Beta (`0.x`) |
| **Format** | Agent Plugins 1.0 (Claude Code and Cursor files generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |

## What's inside

| Component | Name | Portable across IDEs |
| --- | --- | --- |
| Skill | `bicep-avm-review` | Yes |
| Agent | `iac-reviewer` | Copilot namespace; Claude copy generated |
| MCP server | `microsoft-learn` (`streamable-http`) | Yes |

## Install

```text
/plugin install bicep-avm-review --marketplace azurewithdanidu/agentz
```

See [docs/consuming-plugins.md](../../docs/consuming-plugins.md) for other IDEs.

## Usage

Ask: "Review infra/main.bicep against AVM."
