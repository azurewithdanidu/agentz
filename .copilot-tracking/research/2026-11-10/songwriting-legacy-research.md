<!-- markdownlint-disable-file -->
---
description: "Evidence for migrating songwriting to a legacy multi-client plugin."
---

# Songwriting legacy migration research

## Scope and success criteria

Migrate only songwriting, retaining one skill and one logical agent, root-level
components, no Agent Plugins schema, and Copilot, Claude and Cursor manifests.
Keep the other plugins unchanged and retain ownership, version, eval and secret gates.

## Evidence

* `scripts/sync_manifests.py:plugin_files` assumes every root agent is generated and deletes unexpected files.
* `scripts/build_catalog.py:build_catalog` indexes only namespace agents and commands.
* `scripts/validate_repo.py:check_plugin` requires the Agent Plugins schema and checks only namespace agents.
* `check_version_bumps` excludes all root agents as generated, which would miss legacy source changes.
* GitHub's CLI plugin reference documents schema-less root manifests and root `agents/*.agent.md` discovery.
* GitHub's custom-agent configuration reference documents case-insensitive Claude tool aliases.
* Claude's plugin reference discovers root `agents/` Markdown files and skills; its manifest remains in `.claude-plugin/`.

Sources: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference>,
<https://docs.github.com/en/copilot/reference/custom-agents-configuration>,
<https://code.claude.com/docs/en/plugins-reference>.

## Selected approach

The following initial approach was superseded by the rebase update below.

Use a shared root `agents/songwriter.agent.md` with explicit cross-client tool
aliases. Detect format by presence of the canonical schema; reject unsupported
schema declarations. Keep existing Agent Plugins behavior unchanged. For legacy
plugins, preserve authored components and remove only obsolete generated files
whose banners identify the old namespace source. Generate metadata adapters only.

Separate per-client agent copies are unnecessary for this tool subset. No live
IDE verification or model-backed rerun is implied by structural validation.

## Rebase update

The user requested rebasing after shared-file changes reached main. Fetch found
main two commits ahead, with the classic-layout migration in 2ce76c0 and its merge
da88d18. No feature-only commits needed replaying. Main already makes root agents,
commands and skills authored sources and generates only manifest/MCP adapters.
It also requires shared agents to omit tools frontmatter and state limits in the
body. Those upstream conventions replace the initial mixed-format approach.

Retain upstream shared files exactly, retain the songwriting addition and local
ignore rule, and remove redundant interim tests and CI changes. The original
work is preserved in recovery stash bf36534ea22bd90da425486e96aa8bde728e0393.