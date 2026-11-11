# What the setup installs

| Step | Detail |
| --- | --- |
| Python 3.10+ with PyYAML | Needed by the marketplace scripts (`validate_repo.py`, `sync_manifests.py`) |
| Node.js 20+ and Vally 0.20.0 (via `npx`) | Lints and runs the plugin evals |
| Client detection | Lists which of VS Code, Copilot CLI and Claude Code are on the PATH; each is set up only if found |
| VS Code | GitHub Copilot Chat extension. HVE Core is a plugin, not an extension: a manual step (below) |
| Copilot CLI | The `agentz` marketplace, `agentz-publisher`, and `hve-core` from `microsoft/hve-core` unless `--skip-hve` |
| Claude Code | The `agentz` marketplace and `agentz-publisher`. HVE Core is not supported there: reported as `skipped`, and the built-in fallbacks (authoring checklist, eval guide) are used |
| `.agentz/` folder | Git-ignored notes for the publishing phases (only in an agentz clone) |
| Gate check | Runs `validate_repo.py` (only in an agentz clone) |

## Left to do by hand

- VS Code: add `"azurewithdanidu/agentz"` to the `chat.plugins.marketplaces` setting (Experimental), then install `agentz-publisher` from the Plugins view.
- VS Code, for HVE Core: also add `"microsoft/hve-core"` to `chat.plugins.marketplaces` and install `hve-core` from the Plugins view (skip if you don't want HVE Core).
- Cursor: not set up by the script.
