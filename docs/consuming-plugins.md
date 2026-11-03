# Installing plugins

Every client reads the same repository. Users add the marketplace once, then install only the plugins they need.

Plugins are authored in the open Agent Plugins 1.0 format. VS Code and Copilot read it directly; Claude Code and Cursor use files generated from it.

The examples use this repository (`azurewithdanidu/agentz`) and the marketplace name `agentz`. If you fork it, replace both with your own repository and the `name` in `.claude-plugin/marketplace.json`.

## VS Code (GitHub Copilot) — primary

Add the marketplace to user or workspace settings. The setting is marked Experimental.

```json
"chat.plugins.marketplaces": [
  "azurewithdanidu/agentz"
]
```

To pin a version, append a ref: `azurewithdanidu/agentz#v1.4.0`. Then install from the Plugins view in the Agent Customizations editor. VS Code loads each plugin through its root `plugin.json`: skills, MCP servers, and the agents and commands in `com.github.copilot/`.

## GitHub Copilot CLI

```shell
copilot plugin marketplace add azurewithdanidu/agentz
copilot plugin marketplace browse agentz
copilot plugin install bicep-avm-review@agentz
copilot plugin list
```

Copilot CLI reads the marketplace from `.github/plugin/marketplace.json` (generated) and each plugin through its root `plugin.json`. Updates are manual (`copilot plugin update --all`) unless the user opts in to auto-update.

## Claude Code

```text
/plugin marketplace add azurewithdanidu/agentz
/plugin install bicep-avm-review@agentz
```

On Claude Code 2.1.275 or later, one line does both: `/plugin install bicep-avm-review --marketplace azurewithdanidu/agentz`. Browse with `/plugin`. Claude Code reads the generated `.claude-plugin/` files and ignores the Agent Plugins manifest.

Organisation admins can also sync this repository in claude.ai (**Organization settings > Plugins & skills > Sync from GitHub**) and set each plugin to available, installed by default, or required. The repository must be private or internal on github.com.

## Cursor

On Teams and Enterprise plans, an admin adds the repository under **Dashboard > Plugins & MCPs > Team Marketplaces > Import from Repo**, then sets each plugin to Default Off, Default On, or Required. Users install from **Customize** in the sidebar. Auto Refresh needs the Cursor GitHub App on the repository.

Each plugin has both a root `plugin.json` (Agent Plugins) and a generated `.cursor-plugin/plugin.json`. Cursor's docs don't say which wins when both exist. Under Agent Plugins semantics Cursor loads skills and MCP servers only, so check whether agents and commands appear before relying on them in Cursor.

## Pinning and updates

| Tool | Default update behaviour | How to pin |
| --- | --- | --- |
| VS Code | Auto-updates when `extensions.autoUpdate` is on | `owner/repo#ref` |
| Copilot CLI | Manual, unless auto-update is turned on | `owner/repo#ref`, or `sha` on a source |
| Claude Code | Follows the marketplace's default branch | Marketplace `#ref`, or `ref`/`sha` on a plugin source |
| Claude org sync | Syncs on every push to the default branch | Not available; the default branch is what members get |
| Cursor | Manual refresh, or Auto Refresh on push | Not documented |

Because org sync and Auto Refresh follow `main` directly, everything merged to `main` must already have passed the gate.
