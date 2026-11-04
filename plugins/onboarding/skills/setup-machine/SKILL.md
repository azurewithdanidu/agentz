---
name: setup-machine
description: Set up this machine to contribute plugins to the agentz marketplace. Installs agentz-publisher, HVE Core (hve-builder and vally-tests), Python with PyYAML and Vally for the evals. Use when someone wants to start contributing, has just installed onboarding, or runs /init. Do not use to install plugins for normal use, to build a plugin (use agentz-publisher) or to configure unrelated tools.
---

# Set up a machine for plugin contributions

Run the bundled script, show the result, and tell the person what is left to do by hand. The script does the work; this skill previews it, runs it and explains the outcome. It asks no questions about roles or plugin choices.

## Steps

1. **Check the folder.** The person should be in a clone of `azurewithdanidu/agentz` (it has `scripts/validate_repo.py`). If not, say so; the script still installs the tools but skips the repository check.
2. **Dry run first.** Run the script for the OS with `--dry-run` (`-DryRun` on Windows) and show the commands it would run. Wait for a go-ahead.
3. **Run it for real**, with the same options minus the dry-run flag. Pass `--skip-hve` (`-SkipHve`) only if the person said they do not want HVE Core.
4. **Report** what is done, skipped and failed. Always list the VS Code manual step (add the marketplace to `chat.plugins.marketplaces`).
5. **Point to the next step:** run `/new-plugin` or select the `publisher` agent.

## Running the script

The script sits next to this file at `scripts/`. Pick by OS:

| OS | Command |
| --- | --- |
| macOS, Linux, WSL | `bash scripts/setup.sh [--skip-hve] [--hve-ref <ref>] [--dry-run]` |
| Windows | `pwsh scripts/setup.ps1 [-SkipHve] [-HveRef <ref>] [-DryRun]` |

Resolve `scripts/` relative to this skill's folder, not the working directory.

## Rules

- Do not edit the person's VS Code `settings.json` or any shell profile; report the manual step instead.
- HVE Core is optional. The marketplace gate never depends on it, so a skipped or failed HVE Core install does not block publishing.
- If a step fails, show the error and the fix the script printed. Do not retry in a loop.
- See [references/what-it-installs.md](references/what-it-installs.md) for exactly what it changes.
