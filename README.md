# agentz

An agent marketplace by Azure with Danidu: reviewed skills, agents and commands that teams install instead of rebuilding.

One repository, authored once, consumed by **Claude Code**, **VS Code (GitHub Copilot)**, **GitHub Copilot CLI** and **Cursor**.

## Plugins

<!-- plugins-table:start -->
| Plugin | Version | Category | Owner | Skills | Description |
| --- | --- | --- | --- | --- | --- |
| [`bicep-avm-review`](plugins/bicep-avm-review/) | 0.3.1 | development | Azure with Danidu | `bicep-avm-review` | Reviews Bicep templates against Azure Verified Modules (AVM) and organisation conventions, and produces a traceable findings report. |
| [`plugin-creator`](plugins/plugin-creator/) | 1.0.1 | productivity | Azure with Danidu | `create-plugin` | Scaffolds a new plugin that meets the marketplace standard: both manifests, a first skill, an evals file and catalog registration. |
<!-- plugins-table:end -->

This table is generated from `catalog.json` by `scripts/build_catalog.py`.

## Install

```text
/plugin marketplace add azurewithdanidu/agentz
/plugin install <plugin>@agentz
```

Every IDE is covered in [docs/consuming-plugins.md](docs/consuming-plugins.md).

## Contribute

1. Check [catalog.json](catalog.json) for an existing plugin that does the job. Extend it if there is one.
2. Install `plugin-creator` and run `/new-plugin <name>`, or run `plugins/plugin-creator/scripts/scaffold.py`.
3. Follow the [plugin standard](docs/plugin-standard.md) and the [skill authoring standard](docs/skill-authoring-standard.md).
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
| CI (`scripts/validate_repo.py`) | Manifests, naming, version bump, 10+ evals, links, secrets, CODEOWNERS, generated files | Yes |
| CI (`claude plugin validate`) | Anthropic's own marketplace and plugin validator | Yes |
| CI (duplicate check) | Similarity of new skills and agents to existing ones | No, warns |
| Copilot code review | Overlap, skill quality, eval quality, portability, README | No, comments |
| CODEOWNERS approval | Plugin owner and marketplace owner | Yes |

## Repository layout

```text
.claude-plugin/marketplace.json   # source of truth: the plugin registry
.cursor-plugin/marketplace.json   # generated Cursor mirror
catalog.json                      # generated index used for duplicate checks
plugins/<name>/                   # one folder per plugin
scripts/                          # sync, catalog and validation scripts
docs/                             # standards and install guide
.github/                          # CI, CODEOWNERS, Copilot review instructions, PR template
```
