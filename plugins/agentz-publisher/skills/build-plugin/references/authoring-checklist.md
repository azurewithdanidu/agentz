# Authoring checklist (without HVE Core)

The full standard is `docs/skill-authoring-standard.md`. This is the short version.

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
