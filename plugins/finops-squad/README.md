---
title: finops-squad plugin
description: Installable Azure FinOps workflows with evidence and approval gates.
---

## finops-squad

Assess Azure costs, rank opportunities, produce Markdown reports and propose approved Bicep PRs.
Never deploy or mutate live Azure. There is no interactive dashboard.

| Property | Value |
|----------|-------|
| Owner | Azure with Danidu, @azurewithdanidu |
| Version | 1.0.0; publication and runtime validation gates remain |
| Format | Classic plugin with generated Claude Code and Cursor manifests |
| Clients | Copilot CLI clean-consumer loading and safety refusal tested; VS Code, Claude Code and Cursor runtime support unverified |

## Install locally

Point your client's local plugin loader at this directory, not the development repository root.
With Copilot CLI, start a session using:

```powershell
copilot --plugin-dir "D:\path\to\azure-finops-squads\plugins\finops-squad" --agent finops-squad:finops-orchestrator
```

Marketplace installation becomes available only after a source commit is published and a linked
entry is approved in agentz. It is not available from the marketplace yet.

The CLI uses the qualified agent name `finops-squad:finops-orchestrator`, not
`finops-orchestrator`. The observed smoke test disabled MCP, shell, writes and URL access; it
proves plugin loading and permission refusal, not live query availability.

## Prerequisites

- Python 3.10+ and `jsonschema` for the bundled offline scripts
- Git for artifact privacy checks and approved IaC work
- Node.js and npx if using the bundled Microsoft Azure MCP server
- A consumer-local, Git-ignored `.finops/config.json`
- A dedicated Azure identity without effective write access, confirmed by the user before queries

The bundled `finops-azure` MCP server uses Microsoft Azure MCP 3.0.0. If your client already
provides an equivalent server, disable the duplicate server in the client. Installing this
plugin does not guarantee cost querying or any host-specific `arm` capability; discover the
available tools and report gaps honestly.

## Use

Select `finops-orchestrator` or ask:

> Run a read-only FinOps audit using my local configuration. Rank the findings and write reports.
> Do not remediate or open PRs.

Other supported requests include resuming a run, reporting on existing artifacts, preparing a
PR for a specifically approved finding, and verifying a merged finding after settling time.
T3 and untiered findings cannot be remediated. T2 requires separate confirmation and a draft PR.
Confirmation flags in local scripts do not independently prove human consent.

For an offline demonstration, use the synthetic files in `evals/fixtures/legacy/`; do not
mistake them for observations of your subscription.

## Where files live

The plugin supplies skills, Python tools and schemas. It remains unchanged during a run.
Your configuration, evidence and reports stay in your workspace's ignored `.finops/` directory.
The agent must resolve tools from the installed `skills/finops-squad/SKILL.md` location, not
from an assumed `scripts/` directory in your workspace.

Reports are Markdown/JSON files opened directly in the editor: executive summary, engineer
backlog, savings ledger, named KPIs and optional iteration retrospective. Estimates and realised
savings stay separate; currencies are never blended.

## Validation

Development tests live in the source repository's `tests/`. Behavioural plugin evaluations live
in `evals/eval.yaml` and need Vally plus Copilot authentication. Run them only in a disposable,
isolated worker without Azure/AWS credentials, inherited cloud configuration or global user
customisations. Vally's temporary directory is not an OS sandbox, and tool simulations are only
defence in depth. Generated client metadata is not evidence that every client has been live-tested.
