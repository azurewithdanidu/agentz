---
description: "agentz plugin authoring conventions for skills, agents, commands and manifests in the Agent Plugins 1.0 layout; applies when hve-builder or anyone creates or edits plugin files under plugins/."
applyTo: "plugins/**"
---

# agentz authoring conventions

This repository is the agentz plugin marketplace. When creating or changing a skill, agent, command or manifest here (including through HVE Core's `hve-builder`), follow these conventions. They add to the authoring standard; they don't replace safety rules.

## Where things go

- One plugin per folder: `plugins/<plugin-name>/`. Never write to `.github/agents/`, `.github/skills/` or `.github/prompts/` for plugin content.
- Skills: `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`, with `steps/`, `references/`, `templates/`, `scripts/` beside it. The skill folder name equals the frontmatter `name`.
- Agents: `plugins/<plugin-name>/com.github.copilot/agents/<agent-name>.agent.md`.
- Commands: `plugins/<plugin-name>/com.github.copilot/commands/<command-name>.md`.
- MCP servers: `plugins/<plugin-name>/mcp.json` with `$schema` `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json` and `type` `stdio` or `streamable-http`.
- Never create or edit `agents/`, `commands/`, `.claude-plugin/`, `.cursor-plugin/` or `.mcp.json` inside a plugin. `scripts/sync_manifests.py` generates them.

## Skills carry the logic

- Put all domain logic in skills; every client loads skills. Agents and commands stay thin and delegate to a skill.
- Skill descriptions are 50 to 1,024 characters and say what the skill does, "Use when …" with real trigger phrases, and "Do not use …".
- Don't use client-specific variables in skills (for example `$ARGUMENTS` or `${input:…}`).

## Agents

- Frontmatter: `name` (equals the file name without `.agent.md`), `description`, `tools`.
- `tools` may only use `read`, `search`, `edit`, `execute`, `web`, `todo`. These map to Claude Code tools; anything else fails CI.
- Don't set `model:`; plugins run on whatever model the user chose.

## After any change

```bash
python3 scripts/sync_manifests.py
python3 scripts/build_catalog.py
python3 scripts/validate_repo.py
```

Bump `version` in the plugin's root `plugin.json` for every change.
