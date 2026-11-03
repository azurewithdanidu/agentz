# agentz

An agent marketplace by Azure with Danidu: reviewed skills, agents and commands that teams install instead of rebuilding.

One repository, authored once in the open [Agent Plugins 1.0](https://agent-plugins.org) format, consumed by **VS Code (GitHub Copilot)**, **GitHub Copilot CLI**, **Claude Code** and **Cursor**. VS Code is the primary client; Claude Code and Cursor files are generated.

## Plugins

<!-- plugins-table:start -->
| Plugin | Version | Category | Owner | Skills | Description |
| --- | --- | --- | --- | --- | --- |
| [`bicep-avm-review`](plugins/bicep-avm-review/) | 0.4.0 | development | Azure with Danidu | `bicep-avm-review` | Reviews Bicep templates against Azure Verified Modules (AVM) and organisation conventions, and produces a traceable findings report. |
| [`plugin-creator`](plugins/plugin-creator/) | 1.1.0 | productivity | Azure with Danidu | `create-plugin` | Scaffolds a new Agent Plugins 1.0 plugin that meets the marketplace standard: manifest, a first skill, an evals file and catalog registration. |
<!-- plugins-table:end -->

This table is generated from `catalog.json` by `scripts/build_catalog.py`.

## Install

VS Code: add `"azurewithdanidu/agentz"` to the `chat.plugins.marketplaces` setting, then install from the Plugins view.

```text
copilot plugin marketplace add azurewithdanidu/agentz        # Copilot CLI
/plugin marketplace add azurewithdanidu/agentz               # Claude Code
```

Every IDE is covered in [docs/consuming-plugins.md](docs/consuming-plugins.md).

## Contribute

1. Check [catalog.json](catalog.json) for an existing plugin that does the job. Extend it if there is one.
2. Install `plugin-creator` and run `/new-plugin <name>`, or run `plugins/plugin-creator/scripts/scaffold.py`.
3. Follow the [plugin standard](docs/plugin-standard.md) and the [skill authoring standard](docs/skill-authoring-standard.md). Edit only the Agent Plugins sources: `plugin.json`, `mcp.json`, `skills/` and `com.github.copilot/`.
4. Run the checks locally:

   ```bash
   pip install pyyaml
   python3 scripts/sync_manifests.py
   python3 scripts/build_catalog.py
   python3 scripts/validate_repo.py
   ```

5. Open a pull request. CI runs the hard checks, Copilot reviews against the standards, and the plugin owner and the marketplace owner approve.

## How the gate works

| Layer | Checks | Blocks merge |
| --- | --- | --- |
| CI (`scripts/validate_repo.py`) | Agent Plugins manifest and `mcp.json` schema, naming, version bump, 10+ evals, agent tool mapping, links, secrets, CODEOWNERS, generated files | Yes |
| CI (`claude plugin validate`) | Anthropic's validator on the generated Claude files | Yes |
| CI (duplicate check) | Similarity of new skills and agents to existing ones | No, warns |
| Copilot code review | Every rule in `.github/instructions/`: reuse and duplicates, manifest and MCP, skill quality, agents and generated files, eval coverage, changes to the gate | No, comments |
| CODEOWNERS approval | Plugin owner and marketplace owner | Yes |

## Repository layout

```text
.claude-plugin/marketplace.json   # source of truth: the plugin registry
.github/plugin/marketplace.json   # generated for Copilot CLI and VS Code
.cursor-plugin/marketplace.json   # generated for Cursor
catalog.json                      # generated index used for duplicate checks
plugins/<name>/                   # one folder per plugin; root plugin.json is the Agent Plugins manifest
scripts/                          # sync, catalog and validation scripts
docs/                             # standards and install guide
.github/                          # CI, CODEOWNERS, Copilot review instructions, PR template
```
