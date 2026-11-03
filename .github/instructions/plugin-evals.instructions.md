---
applyTo: "plugins/*/evals/**"
---

# Eval rules

Every plugin ships at least 10 eval cases in `evals/evals.yaml`. CI checks the count; you check that the cases are meaningful.

## Required coverage

- Trigger cases that **should** fire, phrased the way real users ask (at least three).
- Trigger cases that **should not** fire on nearby requests, such as a different tool, language or action (at least two).
- Task cases for the skill's real failure modes, not only the happy path. For a review skill, that means specific rule violations it must catch.
- At least one case for each stop condition in the skill (for example: no input files found).
- At least one safety case where relevant (for example: a secret must not be printed).

## Quality

- Each case has a unique `id`, a `type` (`trigger` or `task`), and a concrete `expect`.
- `expect` values are checkable, not vague ("finding AVM-02 with severity High", not "works well").
- Fixtures referenced by task cases exist or are added in the same PR.
- When a skill changes behaviour, its evals change with it. Flag a skill change with no eval change.
- Flag cases that duplicate each other or only restate the description.

The eval format and runner are still being finalised; until then, also ask the author to confirm the evals were run locally.
