<!-- markdownlint-disable-file -->
---
description: "Implementation plan for the songwriting legacy plugin migration."
---

# Songwriting legacy migration plan

## User requests

* Move songwriting away from Agent Plugins 1.0: no namespace folder and no schema in its manifest.
* Retain multi-client support and one songwriting agent plus one English songwriting skill.
* Proceed with implementation after the planning discussion; do not migrate other plugins.
* Rebase onto the latest main and reuse its shared-file and instruction changes.

## Context and dependencies

Follow the repository plugin authoring, manifest, agent, eval, submission and gate
instructions; update their format assumptions without reducing quality checks.
Apply HVE Markdown, writing and prompt-authoring instructions. Use the
agent-customization and python-fact-grounded-coding skills. Python 3.12,
PyYAML and pinned Vally lint are the available validation tools.

Research: `.copilot-tracking/research/2026-11-10/songwriting-legacy-research.md`.
Details: `.copilot-tracking/details/2026-11-10/songwriting-legacy-details.md`.
Log: `.copilot-tracking/plans/logs/2026-11-10/songwriting-legacy-log.md`.

## Implementation checklist

<!-- parallelizable: false -->
* [x] Preserve local work and rebase onto origin/main at da88d18.
* [x] Adopt upstream classic-layout tooling and instructions instead of the interim mixed-format implementation.
* [x] Keep one shared songwriting agent and one skill; follow upstream body-based permission limits.
* [x] Restore local artifacts, regenerate the README table and pass the repository, Vally and Claude gates.

The initial mixed-format implementation and regression tests were superseded by
main's completed classic-layout migration. No local shared-script, workflow or
instruction changes remain. The rebase review records each conflict resolution.

## Success criteria

Songwriting has no namespace folder or manifest schema, exactly one shared agent
source and one skill, preserved client manifests, version 0.2.0, complete catalog
coverage and passing local structural checks. Existing plugin content and eval
requirements remain unchanged. Live IDE and model behavior limitations are disclosed.