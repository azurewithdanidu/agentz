# Authoring checklist

The built-in path for the Build phase. It is the only path in Claude Code, and it is also the check to apply to anything `hve-builder` writes. The full standard is `docs/skill-authoring-standard.md`; this is the short version.

## Layout and manifest rules

- [ ] Everything lives in `plugins/<name>/`; folder name = plugin name = manifest name.
- [ ] Skills in `skills/<skill>/SKILL.md` (folder name = frontmatter `name`); agents in `agents/<name>.agent.md`; commands in `commands/<name>.md`; MCP in `.mcp.json`.
- [ ] Never hand-edit generated files: `.claude-plugin/`, `.cursor-plugin/`, `mcp.json`. Run `scripts/sync_manifests.py` instead.
- [ ] No `com.github.copilot/` folder, no `$schema` or `extensions` in the root `plugin.json`, no top-level `bin/`.
- [ ] Agents have `name` and `description` only: no `tools` list, no `model`. State limits (for example read-only) in the body.
- [ ] Logic lives in the skill; agents and commands stay thin and delegate to it. No client-specific variables (`$ARGUMENTS`, `${input:...}`) in skills.
- [ ] Bump `version` in the root `plugin.json` for every change.

## Description

- [ ] What the skill does, in one sentence.
- [ ] "Use when …" with the brief's trigger phrases, as a user would type them.
- [ ] "Do not use …" with the brief's non-trigger cases.
- [ ] 50 to 1,024 characters.

## SKILL.md body

- [ ] When to use and when not to use.
- [ ] Inputs, prerequisites and permissions.
- [ ] An ordered workflow that names the supporting file to read at each step.
- [ ] Approval gates, stop conditions and safety boundaries.
- [ ] Outputs and how you know it's done.
- [ ] Which actions it may take: report only, edit files, run local checks, change external systems.

## Supporting files

- [ ] Long procedures in `steps/`, rules and mappings in `references/`, output formats in `templates/`, deterministic checks in `scripts/`.
- [ ] One copy of each rule, linked from wherever it's needed.
- [ ] Every relative link resolves.
