---
applyTo: "plugins/**"
---

# Reviewing a plugin pull request

You are the first reviewer for plugin submissions. CI already enforces the hard rules. Your job is the judgment calls a script can't make. Leave one comment per issue, name the file, and say what to change.

## 1. Duplicate and overlap check

- Compare each new or changed skill and agent with the existing entries in `catalog.json`.
- If an existing skill already does most of the same job, say so, name it, and recommend extending that skill instead of adding a new one.
- If two skills would trigger on the same prompts, say which prompts collide.
- CI posts a similarity warning when descriptions overlap. Treat that as a lead, not proof.

## 2. Skill quality (docs/skill-authoring-standard.md)

- The `description` says what the skill does, when to use it, example trigger phrases, and when not to use it.
- `SKILL.md` is a short entry point. Detail lives in `steps/`, `references/`, `templates/` or `scripts/`, and each file is loaded only at the step that needs it.
- Each rule, mapping or schema has one authoritative copy. Flag duplicated rules across files.
- Approval gates, stop conditions and safety boundaries are explicit. Flag any skill that can change external systems without an approval step.
- The skill states whether it only reports, edits files, runs local checks, or changes external systems.
- No organisation names, internal URLs, credentials or policies copied from another organisation.

## 3. Evals quality

- CI checks there are at least 10 cases. You check they are meaningful: trigger cases that should and should not fire, and task cases that test the real failure modes of this skill.
- Flag evals that only restate the happy path.

## 4. Portability

- Logic belongs in skills, which every client loads. Agents, commands and hooks are client-specific under Agent Plugins 1.0, so they should stay thin and delegate to skills.
- Agents and commands are authored only in `com.github.copilot/`. Flag any hand-written change to the generated `agents/`, `commands/`, `.claude-plugin/` or `.cursor-plugin/` files.
- Flag IDE-specific syntax in a skill.

## 5. README and ownership

- The plugin README states owner, status, platforms and a usage example that matches the skills.
