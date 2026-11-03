# Skill authoring standard

How to write a skill for this marketplace. Copilot review checks submissions against this page.

## 1. Inspect before you write

1. Search `catalog.json` for a skill that already does the job. Extend it if one exists.
2. Read the skills already in the marketplace and follow their naming, layout and writing style.
3. If you are adapting a skill from another organisation, keep only its structure and workflow. Remove its organisation names, internal products, team names, access models, paths, URLs, commands and policies. Don't invent replacements: use placeholders and mark them **to confirm**.

## 2. The entry point: SKILL.md

`SKILL.md` is how the agent discovers the skill and how it controls the workflow. Keep it short.

It must include:

- **Frontmatter:** `name` (lowercase-hyphenated, matching the folder) and `description`.
- **A description that triggers correctly:** what the skill does, when to use it, example trigger phrases, and when not to use it. This is the single biggest factor in whether the skill fires.
- **When to use and when not to use.**
- **Inputs, assumptions, permissions and prerequisites.**
- **The ordered workflow,** naming which supporting file to read at each step.
- **Approval gates, stop conditions and safety boundaries.**
- **Outputs and completion criteria.**
- **Relative links** to supporting files.

Use progressive loading: tell the agent which file it needs at each stage so it doesn't load everything up front.

## 3. Supporting files

Add them only when they make the workflow clearer or more reliable.

| Folder | Holds |
| --- | --- |
| `steps/` | Ordered procedures. Each states purpose, inputs, actions, output, stop conditions and dependencies on other steps. |
| `references/` | Stable material: mappings, rules, schemas, security guidance, links to authoritative docs. |
| `templates/` | Output formats the skill must follow. |
| `scripts/` | Deterministic checks or transformations where code is more reliable than prose. |

Keep one authoritative copy of each rule, schema or mapping, and link to it. Every referenced file must exist and agree with `SKILL.md`.

## 4. Evidence and boundaries

- Inspect the actual repository and evidence before drawing conclusions.
- Separate confirmed facts, assumptions, open decisions and missing evidence.
- Give every important finding a traceable source: a path, a config value, a decision, or a documented reference.
- Don't infer runtime behaviour from file names alone.
- State what is in scope and out of scope.
- If a prerequisite is missing, skip the action and say why.
- Separate assessment and planning from implementation.
- Put edits, deployments, data movement and changes to external systems behind explicit approval.
- Never expose secrets. Don't create credentials or run privileged operations unless policy allows it.
- Don't claim success without the verification evidence the skill defines.

## 5. Declare what the skill may do

State which of these apply:

- Produces findings or plans only.
- May edit repository files.
- May run local validation.
- May contact or change external systems.
- Needs approval before moving to the next phase.

## 6. Evals

Write at least 10 stimuli in `evals/eval.yaml` ([Vally](https://www.npmjs.com/package/@microsoft/vally-cli) format). The full guide, with grader choices and an example, is `plugins/agentz-publisher/skills/validate-plugin/references/eval-guide.md`. With HVE Core installed, `vally-tests` can draft them from your `SKILL.md`.

- **Trigger cases** that should fire, and that should not fire on nearby requests.
- **Task cases** that test the skill's real failure modes, not just the happy path.

## 7. Before you open the PR

- Frontmatter is valid and `name` matches the folder.
- The description is specific enough to trigger correctly.
- Every referenced file exists and is reachable from the workflow.
- Steps, gates, stop conditions and outputs agree across files.
- No source-organisation details remain.
- Scripts suit the target environment, and read-only checks are separate from changes.
- `python3 scripts/validate_repo.py` passes.
