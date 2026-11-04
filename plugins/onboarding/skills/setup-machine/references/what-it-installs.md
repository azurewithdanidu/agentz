# What the setup installs

| Step | Detail |
| --- | --- |
| Python 3.10+ with PyYAML | Needed by the marketplace scripts (`validate_repo.py`, `sync_manifests.py`) |
| Node.js 20+ and Vally 0.20.0 (via `npx`) | Lints and runs the plugin evals |
| VS Code extensions | GitHub Copilot Chat, and the HVE Core extension (`ise-hve-essentials.hve-core`) unless `--skip-hve` |
| Copilot CLI | The `agentz` marketplace, `agentz-publisher`, and `hve-core` from `microsoft/hve-core` unless `--skip-hve` |
| Claude Code | The `agentz` marketplace and `agentz-publisher`. HVE Core is not available there |
| `.agentz/` folder | Git-ignored notes for the publishing phases (only in an agentz clone) |
| Gate check | Runs `validate_repo.py` (only in an agentz clone) |

## Left to do by hand

- VS Code: add `"azurewithdanidu/agentz"` to the `chat.plugins.marketplaces` setting (Experimental), then install `agentz-publisher` from the Plugins view.
- Cursor: not set up by the script.
