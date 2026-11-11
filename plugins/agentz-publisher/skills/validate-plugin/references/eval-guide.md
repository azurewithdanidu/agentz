# Writing agentz evals

Evals use the [Vally](https://www.npmjs.com/package/@microsoft/vally-cli) `eval.yaml` format, one file per plugin at `plugins/<name>/evals/eval.yaml`. Each case (a **stimulus**) is a concrete input with checkable expectations (**graders**).

## Minimums (enforced by CI)

| Case type | Minimum | Tag | Main grader |
| --- | --- | --- | --- |
| Should trigger | 3, and at least one per skill | `kind: trigger` | `skill-invocation` with `required: [<skill>]` |
| Should not trigger | 2 | `kind: no-trigger` | `skill-invocation` with `disallowed: [<skill>]` |
| Task (real failure modes) | rest of the 10 | `kind: task` | `output-matches`, `file-matches`, `diff-empty` |
| Stop condition | 1 per stop condition, where testable | `kind: stop` | `output-matches`, `diff-empty` |
| Safety | 1 where relevant | `kind: safety` | `output-not-contains`, `tool-calls` with `disallowed` |

Total: at least 10 stimuli.

## Drafting stimuli by hand

Do this when HVE Core's `vally-tests` isn't available (Claude Code) or to review its draft.

1. Copy the intent brief's trigger phrases into `kind: trigger` stimuli, one per phrase, with `skill-invocation` and `required`. Cover every skill in the plugin.
2. Copy the brief's non-trigger cases into `kind: no-trigger` stimuli with `skill-invocation` and `disallowed`.
3. For each failure mode in the brief, write a `kind: task` stimulus with a prompt that would expose it and a deterministic grader for the good answer (a regex naming the expected finding, a file that must exist, text that must be absent).
4. For each stop condition and approval gate in `SKILL.md`, write a `kind: stop` or `kind: safety` stimulus (for example "refuses to write outside the plugin folder").
5. Count against the minimums, give every stimulus a unique `name`, and tag `kind` and `skill`.
6. Lint, then check each regex is not so loose that any answer passes (a pattern like `not` matches almost everything).

## Picking graders

| To check | Grader |
| --- | --- |
| The right skill fired | `skill-invocation` with `required` |
| The skill stayed out of a nearby request | `skill-invocation` with `disallowed` |
| A specific finding or phrase in the answer | `output-matches` (regex) or `output-contains` |
| A secret or forbidden text is absent | `output-not-contains` |
| Nothing was written (read-only skills) | `diff-empty` |
| A tool was or wasn't used | `tool-calls` with `required` or `disallowed` |
| A file was created with the right content | `file-exists`, `file-matches` |
| Open-ended quality | `prompt` (judge model) with a `rubric` list; use sparingly |

Prefer deterministic graders. A judge model costs more and varies between runs.

## Fixtures

Stage input files with `agent_environment.files` (`src` relative to `eval.yaml`, `dest` inside the workspace). Keep fixtures small and fake: no real secrets, hostnames or customer data.

## Writing good cases

- Phrase trigger prompts the way users really ask, taken from the intent brief.
- Make every expectation checkable: "reports AVM-02 at High", not "gives a good review".
- Test failure modes, not just the happy path.
- When the skill's behaviour changes, change its evals in the same PR.

## Example

```yaml
name: my-plugin
description: Evals for my-plugin.
type: capability
defaults:
  runs: 3
  timeout: 3m
agent_environment:
  skills:
    - ../skills/my-skill
scoring:
  threshold: 0.7
stimuli:
  - name: trigger-review-request
    prompt: Review main.bicep against AVM.
    tags: { kind: trigger, skill: my-skill }
    graders:
      - type: skill-invocation
        config: { required: [my-skill] }
```
