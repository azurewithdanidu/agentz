# agentz-publisher

Guides contributors from an idea to a published plugin in four phases. Start here when you want to share an agent or skill with other teams.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Stable (`2.x`); replaces `plugin-creator` |
| **Format** | Agent Plugins 1.0 (Claude Code and Cursor files generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |
| **Works with** | HVE Core (`hve-builder`, `vally-tests`), optional |

## The four phases

| Phase | Skill | Output |
| --- | --- | --- |
| 1. Analyse | `analyse-request` | `.agentz/<name>/intent-brief.md` |
| 2. Research | `research-catalog` | `.agentz/<name>/research.md` with a reuse, extend or new verdict |
| 3. Build | `build-plugin` | The plugin folder, authored with `hve-builder` when HVE Core is installed |
| 4. Validate | `validate-plugin` | Vally evals, a passing gate, `.agentz/<name>/readiness-report.md`, then a PR |

## What's inside

| Component | Name | Portable across clients |
| --- | --- | --- |
| Skills | `analyse-request`, `research-catalog`, `build-plugin`, `validate-plugin` | Yes |
| Agent | `publisher` | Copilot namespace; Claude copy generated |
| Commands | `/new-plugin`, `/agentz-init` | Copilot namespace; Claude copy generated |
| Scripts | `scripts/scaffold.py`, `skills/research-catalog/scripts/search_catalog.py` | Yes (Python 3.10+, standard library) |

## Install

```text
/plugin install agentz-publisher --marketplace azurewithdanidu/agentz
```

See [docs/consuming-plugins.md](../../docs/consuming-plugins.md) for other clients. To set up everything a contributor needs, run `/agentz-init` or `scripts/init.sh` from the repository root.

## Usage

```text
/new-plugin a skill that reviews Terraform modules against our naming rules
```

Or select the **publisher** agent and describe what you want to share.
