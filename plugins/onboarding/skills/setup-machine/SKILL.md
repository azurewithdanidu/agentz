---
name: setup-machine
description: Set up this machine to use or contribute to the agentz marketplace. Adds the marketplace to VS Code, Copilot CLI and Claude Code, installs chosen plugins, and for contributors installs Python, Vally and HVE Core. Use when someone has just installed onboarding, asks to get started with agentz, or runs /init. Do not use to build a plugin (use agentz-publisher) or to configure unrelated tools.
---

# Set up a machine for agentz

Run the bundled script for the person's role, show them the result, and tell them what is left to do by hand. The script does the work; this skill decides which options to pass and explains the outcome.

## Steps

1. **Ask the role.** Is the person a *user* (installs plugins) or a *contributor* (publishes plugins)? Default to user. A contributor must run from a clone of `azurewithdanidu/agentz`, so check the working directory has `scripts/validate_repo.py`; if not, say so and offer to continue as a user.
2. **Ask which plugins** a user wants, if any. List them with `copilot plugin marketplace browse agentz` or `/plugin`. Never install a plugin the person did not ask for.
3. **Dry run first.** Run the script for the OS with `--dry-run` (`-DryRun` on Windows) and show the commands it would run. Wait for a go-ahead.
4. **Run it for real**, same options without the dry-run flag.
5. **Report**: what is done, what was skipped and why, and what failed. Always list the VS Code manual step (add the marketplace to `chat.plugins.marketplaces`).

## Running the script

The script sits next to this file at `scripts/`. Pick by OS:

| OS | Command |
| --- | --- |
| macOS, Linux, WSL | `bash scripts/setup.sh [--role user\|contributor] [--plugins a,b] [--skip-hve] [--hve-ref <ref>] [--dry-run]` |
| Windows | `pwsh scripts/setup.ps1 [-Role user\|contributor] [-Plugins a,b] [-SkipHve] [-HveRef <ref>] [-DryRun]` |

Resolve `scripts/` relative to this skill's folder, not the working directory.

## Rules

- Do not edit the person's VS Code `settings.json` or any shell profile; report the manual step instead.
- Do not install HVE Core unless the person is a contributor and has not asked to skip it. HVE Core is optional: the marketplace gate never depends on it.
- If a step fails, show the error and the fix the script printed. Do not retry in a loop.
- See [references/what-it-installs.md](references/what-it-installs.md) for exactly what each role changes.
