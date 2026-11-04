# What each role installs

| Step | User | Contributor |
| --- | --- | --- |
| Add the `agentz` marketplace to Copilot CLI and Claude Code (when installed) | Yes | Yes |
| Install the plugins named with `--plugins` | Yes | Yes |
| Install `agentz-publisher` | No | Yes |
| VS Code: GitHub Copilot Chat extension | Yes | Yes |
| VS Code: HVE Core extension (`ise-hve-essentials.hve-core`) | No | Yes, unless `--skip-hve` |
| Copilot CLI: `hve-core` plugin from `microsoft/hve-core` | No | Yes, unless `--skip-hve` |
| Python 3.10+ with PyYAML | No | Yes |
| Node.js 20+ and Vally 0.20.0 (via `npx`) | No | Yes |
| `.agentz/` working folder and a gate check (only in an agentz clone) | No | Yes |

## Left to do by hand

- VS Code: add `"azurewithdanidu/agentz"` to the `chat.plugins.marketplaces` setting (Experimental), then install plugins from the Plugins view.
- Cursor: team marketplaces are configured by an admin in the Cursor dashboard.
- Claude Code: HVE Core is not available there; use VS Code or Copilot CLI for `hve-builder` and `vally-tests`.
