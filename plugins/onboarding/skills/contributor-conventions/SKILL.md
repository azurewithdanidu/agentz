---
name: contributor-conventions
description: The agentz rules for creating or editing plugin content under plugins/ - folder layout, skill, agent and command conventions, Vally eval rules and the commands to run after a change. Use when someone creates or changes a skill, agent, command, manifest or eval in agentz, asks where a plugin file goes, how to write evals, or what the CI gate requires. Do not use to set up a machine (use setup-machine), to run the publishing flow (use agentz-publisher) or to install plugins for normal use.
---

# agentz contributor conventions

These rules apply to every client (VS Code, Copilot CLI, Claude Code, Cursor) and to any tool that writes plugin files, including HVE Core's `hve-builder` and `vally-tests`. They add to the authoring standard; they don't replace safety rules.

Read the reference that matches the task, then follow it:

- Creating or changing a skill, agent, command or manifest: [references/authoring.md](references/authoring.md)
- Writing or changing evals: [references/evals.md](references/evals.md)

## Always

- Work only inside `plugins/<plugin-name>/`. Never write plugin content to `.github/agents/`, `.github/skills/` or `.github/prompts/`.
- Never hand-edit generated files (`.claude-plugin/`, `.cursor-plugin/`, `mcp.json` in a plugin; the root catalog and marketplace copies).
- Bump `version` in the plugin's root `plugin.json` for every change.
- After any change, run from the repository root:

```bash
python3 scripts/sync_manifests.py
python3 scripts/build_catalog.py
python3 scripts/validate_repo.py
```
