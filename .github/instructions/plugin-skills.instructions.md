---
applyTo: "plugins/*/skills/**"
---

# Skill rules

Skills are the only component every client loads, so all plugin logic belongs here.

## Frontmatter

- `name` matches the skill folder name: lowercase letters, digits and hyphens, at most 64 characters.
- `description` is 50 to 1,024 characters and states: what the skill does, when to use it (with example trigger phrases), and when not to use it. A weak description is the most common reason a skill fails to trigger. Flag vague or generic descriptions.

## SKILL.md structure

`SKILL.md` is a short entry point. It must include:

- When to use and when not to use.
- Inputs, prerequisites and permissions.
- An ordered workflow that names which supporting file to read at each step (progressive loading).
- Approval gates, stop conditions and safety boundaries.
- Outputs and completion criteria.
- Which of these the skill may do: report only, edit files, run local checks, change external systems.

Flag a `SKILL.md` that contains long procedures, rule tables or schemas inline; those belong in supporting files.

## Supporting files

- `steps/`: ordered procedures, each with purpose, inputs, actions, output and stop conditions.
- `references/`: rules, mappings, schemas. Exactly one copy of each rule; flag rules repeated across files.
- `templates/`: output formats. `scripts/`: deterministic checks.
- Every relative link resolves, and every supporting file is reachable from the workflow.

## Safety and evidence

- Edits, deployments, data movement and external changes sit behind an explicit approval step.
- Findings cite a source (file and line, config value, or documented reference) and separate confirmed facts from assumptions.
- No secrets printed, no credentials created, no privileged operations unless stated as allowed.
- No client-specific syntax in a skill (for example Claude-only or Copilot-only variables).
