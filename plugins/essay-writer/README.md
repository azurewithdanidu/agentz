# essay-writer

Plans, drafts and reviews essays to a shared house style. It always outlines first and asks for approval before drafting, and it never invents sources. Read-only unless you give it a path to save to.

| | |
| --- | --- |
| **Owner** | Azure with Danidu (`@azurewithdanidu`) |
| **Status** | Beta (`0.x`) |
| **Format** | Agent Plugins 1.0 (Claude Code and Cursor files generated) |
| **Platforms** | VS Code (Copilot), Copilot CLI, Claude Code, Cursor |

## What's inside

| Component | Name | Portable across IDEs |
| --- | --- | --- |
| Skill | `essay-writer` | Yes |
| Instructions | `references/house-style.md` (inside the skill, rules ESS-01 to ESS-07) | Yes |
| Agent | `essay-coach` | Copilot namespace; Claude copy generated |

The writing instructions live inside the skill, not in a client-specific rules file, so every IDE gets the same rules.

## Install

```text
# Copilot CLI
copilot plugin marketplace add azurewithdanidu/agentz
copilot plugin install essay-writer@agentz
# Claude Code
/plugin marketplace add azurewithdanidu/agentz
/plugin install essay-writer@agentz
```

See [docs/consuming-plugins.md](../../docs/consuming-plugins.md) for other IDEs.

## Usage

- "Write an essay on whether cities should ban cars." You get an outline first.
- "Review drafts/essay.md." You get a findings report with rule IDs.

## Why it isn't a duplicate

No other plugin in the marketplace covers writing. The only other skills review Bicep and publish plugins.

## Evals

`evals/eval.yaml` has 14 test cases: triggers, near-miss non-triggers, tasks with a fixture, a safety check for secrets, and stop conditions. Run:

```bash
npx -y @microsoft/vally-cli@0.20.0 eval --eval-spec plugins/essay-writer/evals/eval.yaml --require-pass
```
