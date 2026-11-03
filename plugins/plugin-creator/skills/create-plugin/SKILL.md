---
name: create-plugin
description: Scaffold a new plugin for the central marketplace so it meets the marketplace standard from the start. Use when the user says "create a plugin", "new plugin", "scaffold a skill for the marketplace", "publish my agent to the marketplace", or wants to start contributing a plugin. Do not use to edit an existing plugin's logic or to install plugins.
---

# Create a plugin

Creates a new plugin folder with everything the marketplace gate checks for, and registers it in the root marketplace.

## When to use

- Someone wants to contribute a new plugin, skill or agent to the central marketplace.

## When not to use

- Changing an existing plugin. Edit it directly and bump its version.
- Installing plugins. Point the user to `docs/consuming-plugins.md`.

## Inputs

- **Plugin name:** lowercase and hyphenated, 64 characters or fewer.
- **Description:** one or two sentences saying what it does.
- **Owner:** team name, email and GitHub team handle.
- **Category:** one of `productivity`, `development`, `security`, `observability`.
- **First skill name and description.**

Ask for any missing input. Do not invent an owner.

## Workflow

1. **Check for duplicates first.** Read `catalog.json` at the repo root. If an existing plugin or skill does the same job, show it to the user and suggest contributing to it instead. Continue only if the user confirms the new plugin is different.
2. **Scaffold.** Run:

   ```bash
   python3 plugins/plugin-creator/scripts/scaffold.py \
     --name <name> --description "<description>" \
     --owner-name "<team>" --owner-email <email> --owner-handle @<org>/<team> \
     --category <category> \
     --skill <skill-name> --skill-description "<skill description>"
   ```

3. **Generate the mirrors.** Run `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`.
4. **Validate.** Run `python3 scripts/validate_repo.py`. Fix anything it reports.
5. **Hand over.** Tell the user what to fill in next: the skill workflow, at least 10 evals, and the plugin README.

## Stop conditions

- The name already exists in the marketplace: stop and say so.
- The user hasn't confirmed an overlap check result: do not scaffold.

## Output

A new folder under `plugins/<name>/`, a new entry in `.claude-plugin/marketplace.json`, a CODEOWNERS line, and a passing `validate_repo.py` run (apart from the eval count, which the author completes).
