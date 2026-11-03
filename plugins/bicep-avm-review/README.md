# bicep-avm-review

Reviews Bicep templates against Azure Verified Modules (AVM) and organisation IaC conventions. Produces a findings report with evidence. Read-only: it never edits files or deploys.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Beta (`0.x`) |
| **Platforms** | Claude Code, VS Code (Copilot), Copilot CLI, Cursor |

## What's inside

| Component | Name | Portable across IDEs |
| --- | --- | --- |
| Skill | `bicep-avm-review` | Yes |
| Agent | `iac-reviewer` | Varies by IDE |
| MCP server | `microsoft-learn` | Yes |

## Install

```text
/plugin install bicep-avm-review --marketplace azurewithdanidu/agentz
```

See [docs/consuming-plugins.md](../../docs/consuming-plugins.md) for other IDEs.

## Usage

Ask: "Review infra/main.bicep against AVM."
