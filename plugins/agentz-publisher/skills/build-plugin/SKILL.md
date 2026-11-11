---
name: build-plugin
description: Build a new agentz marketplace plugin from a confirmed intent brief, scaffolding the classic plugin layout and authoring its skill, using HVE Core's hve-builder where it is supported, or the built-in checklist everywhere else. Use when the user says "create a plugin", "new plugin", "scaffold a skill for the marketplace", or after research-catalog returns a "new" verdict. This is phase 3 of 4 (Analyse, Research, Build, Validate). Do not use to edit an existing plugin's logic or to install plugins.
---

# Build the plugin

Creates the plugin folder, registers it in the marketplace, and writes the skill from the intent brief. The Claude Code and Cursor manifests are generated afterwards; you never write them by hand.

## When to use

- After `research-catalog` returned **new** for this brief.
- When someone asks to create a new plugin and has a confirmed brief.

## When not to use

- Without a research verdict of **new**. Run `research-catalog` first.
- Changing an existing plugin. Edit it directly and bump its version.

## Inputs

- `.agentz/<plugin-name>/intent-brief.md` (confirmed) and `.agentz/<plugin-name>/research.md` (verdict **new**).
- Owner name, email and GitHub handle, from the brief.
- Category: one of `productivity`, `development`, `security`, `observability`.

## Workflow

1. **Check the gate.** Confirm the research verdict is **new**. If it isn't, stop.
2. **Scaffold.** From the repository root, run:

   ```bash
   python3 plugins/agentz-publisher/scripts/scaffold.py \
     --name <name> --description "<description>" \
     --owner-name "<team>" --owner-email <email> --owner-handle @<handle> \
     --category <category> \
     --skill <skill-name> --skill-description "<skill description>"
   ```

   The skill description must state what it does, when to use it with the brief's trigger phrases, and when not to use it.
3. **Author the skill.** Choose one:
   - **HVE Core installed:** run `hve-builder` with `targets=plugins/<name>/skills/<skill-name>/SKILL.md`, `mode=create`, and the intent brief as `requirements`. The repository's `agentz-authoring` instructions load automatically and keep it inside the agentz layout. Treat the HVE Builder Reviewer's findings as suggestions and verify each one.
   - **Without HVE Core (always the case in Claude Code):** write the skill yourself following [references/authoring-checklist.md](references/authoring-checklist.md). This is a supported path, not a degraded one: the gate checks the same things either way. Say which path you took in the readiness report.
4. **Add an agent or command only if the brief needs one.** Agents go in `agents/<name>.agent.md` with `name` and `description` only (no `tools` list, because Copilot and Claude Code name tools differently; state limits in the body); commands in `commands/<name>.md`. Keep them thin and delegate to the skill.
5. **Generate.** Run `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`.
6. **Hand over** to `validate-plugin`. The scaffold creates one example eval; Validate writes the rest.

## Stop conditions

- The plugin name already exists: stop and say so.
- The brief has no owner: ask. Never invent an owner.

## Output

- `plugins/<name>/` with `plugin.json`, the skill, `evals/eval.yaml`, `README.md`; a marketplace entry; a CODEOWNERS line; generated client files.
- **Done when:** `python3 scripts/validate_repo.py` passes everything except the eval count.
