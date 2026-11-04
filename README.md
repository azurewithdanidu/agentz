# agentz

An agent marketplace by Azure with Danidu: reviewed skills, agents and commands that teams install instead of rebuilding.

One repository, authored once in the open [Agent Plugins 1.0](https://agent-plugins.org) format, consumed by **VS Code (GitHub Copilot)**, **GitHub Copilot CLI**, **Claude Code** and **Cursor**. VS Code is the primary client; Claude Code and Cursor files are generated.

## Plugins

<!-- plugins-table:start -->
| Plugin | Version | Category | Owner | Skills | Description |
| --- | --- | --- | --- | --- | --- |
| [`agentz-publisher`](plugins/agentz-publisher/) | 2.1.0 | productivity | Azure with Danidu | `analyse-request`, `build-plugin`, `research-catalog`, `validate-plugin` | Guides contributors through publishing to the agentz marketplace in four phases: Analyse the idea, Research the catalog for duplicates, Build with HVE Core, and Validate with evals before opening a pull request. |
| [`bicep-avm-review`](plugins/bicep-avm-review/) | 0.5.0 | development | Azure with Danidu | `bicep-avm-review` | Reviews Bicep templates against Azure Verified Modules (AVM) and organisation conventions, and produces a traceable findings report. |
| [`onboarding`](plugins/onboarding/) | 0.1.0 | productivity | Danidu Weerasinghe | `setup-machine` | Sets up a machine for the agentz marketplace: adds it to every installed client, installs plugins, and prepares contributors |
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
2. Set up your machine: install the `onboarding` plugin and run `/init`, choosing *contributor*. It installs PyYAML, Vally, HVE Core and `agentz-publisher`, and skips anything you don't have. Without the plugin, run `plugins/onboarding/skills/setup-machine/scripts/setup.sh --role contributor` (or `setup.ps1 -Role contributor` on Windows) from a clone.
3. Run `/new-plugin <idea>` or select the **publisher** agent. It walks you through Analyse, Research, Build and Validate, using HVE Core's `hve-builder` and `vally-tests` when they're installed.
4. Follow the [plugin standard](docs/plugin-standard.md) and the [skill authoring standard](docs/skill-authoring-standard.md). Edit only the Agent Plugins sources: `plugin.json`, `mcp.json`, `skills/` and `com.github.copilot/`.
5. Run the checks locally:

   ```bash
   pip install pyyaml
   python3 scripts/sync_manifests.py
   python3 scripts/build_catalog.py
   python3 scripts/validate_repo.py
   npx -y @microsoft/vally-cli@0.20.0 lint plugins --eval-spec plugins --strict
   ```

6. Open a pull request. CI runs the hard checks, Copilot reviews against the standards, and the plugin owner and the marketplace owner approve.

## How the gate works

| Layer | Checks | Blocks merge |
| --- | --- | --- |
| CI (`scripts/validate_repo.py`) | Agent Plugins manifest and `mcp.json` schema, naming, version bump, 10+ evals, agent tool mapping, links, secrets, CODEOWNERS, generated files | Yes |
| CI (`claude plugin validate`) | Anthropic's validator on the generated Claude files | Yes |
| CI (`vally lint`) | Eval specs and skills are well-formed | Yes |
| CI (`vally eval`) | Evals for changed plugins pass (needs `COPILOT_GITHUB_TOKEN`) | Yes |
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
