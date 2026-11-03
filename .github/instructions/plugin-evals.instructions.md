---
applyTo: "plugins/*/evals/**"
---

# Eval rules

Every plugin ships Vally evals in `plugins/<name>/evals/eval.yaml`. CI checks the structure, minimums and `vally lint`; you check that the cases are meaningful.

## Required coverage

- Should-trigger stimuli (`skill-invocation` with `required`), phrased the way real users ask: at least three, and every skill covered.
- Should-not-trigger stimuli (`skill-invocation` with `disallowed`) on nearby requests, such as a different tool, language or action: at least two.
- Task cases for the skill's real failure modes, not only the happy path. For a review skill, that means specific rule violations it must catch.
- A case for each stop condition the skill defines, and a safety case where relevant (for example: a secret must not appear in the output).

## Quality

- Each stimulus has a unique `name`, a `prompt` (the input) and graders (the expected result).
- Expectations are checkable: `output-matches` for "AVM-02 at High", not a vague judge rubric. Use a `prompt` judge only for open-ended quality.
- Read-only skills include `diff-empty`.
- Fixtures referenced in `agent_environment.files` exist, are small, and contain no real secrets or customer data.
- When a skill changes behaviour, its evals change with it. Flag a skill change with no eval change.
- Flag stimuli still tagged `advisory: true`, cases that duplicate each other, and cases that only restate the description.
