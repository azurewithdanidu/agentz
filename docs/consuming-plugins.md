# Installing plugins

Every IDE reads the same repository. Users add the marketplace once, then install only the plugins they need.

The examples use this repository (`azurewithdanidu/agentz`) and the marketplace name `agentz`. If you fork it, replace both with your own repository and the `name` in `.claude-plugin/marketplace.json`.

## Claude Code

```text
/plugin marketplace add azurewithdanidu/agentz
/plugin install bicep-avm-review@agentz
```

On Claude Code 2.1.275 or later, one line does both: `/plugin install bicep-avm-review --marketplace azurewithdanidu/agentz`. Browse with `/plugin`. Organisation admins can also sync this repository in claude.ai (**Organization settings > Plugins & skills > Sync from GitHub**) and set each plugin to available, installed by default, or required. The repository must be private or internal on github.com.

## GitHub Copilot CLI

```shell
copilot plugin marketplace add azurewithdanidu/agentz
copilot plugin marketplace browse agentz
copilot plugin install bicep-avm-review@agentz
copilot plugin list
```

Copilot CLI reads `.claude-plugin/marketplace.json` as a fallback location, so no extra manifest is needed. Updates are manual (`copilot plugin update --all`) unless the user opts in to auto-update.

## VS Code (GitHub Copilot)

Add the marketplace to user or workspace settings. The setting is marked Experimental.

```json
"chat.plugins.marketplaces": [
  "azurewithdanidu/agentz"
]
```

To pin a version, append a ref: `azurewithdanidu/agentz#v1.4.0`. Then install from the Plugins view in the Agent Customizations editor.

## Cursor

Cursor reads the generated `.cursor-plugin/` files. On Teams and Enterprise plans, an admin adds the repository under **Dashboard > Plugins & MCPs > Team Marketplaces > Import from Repo**, then sets each plugin to Default Off, Default On, or Required. Users install from **Customize** in the sidebar. Auto Refresh needs the Cursor GitHub App on the repository.

## Pinning and updates

| Tool | Default update behaviour | How to pin |
| --- | --- | --- |
| Claude Code | Follows the marketplace's default branch | Marketplace `#ref`, or `ref`/`sha` on a plugin source |
| Claude org sync | Syncs on every push to the default branch | Not available; the default branch is what members get |
| Copilot CLI | Manual, unless auto-update is turned on | `owner/repo#ref`, or `sha` on a source |
| VS Code | Auto-updates when `extensions.autoUpdate` is on | `owner/repo#ref` |
| Cursor | Manual refresh, or Auto Refresh on push | Not documented |

Because org sync and Auto Refresh follow `main` directly, everything merged to `main` must already have passed the gate.
