# agentz eval conventions

When writing Vally evals for a plugin in this repository (including through HVE Core's `vally-tests`), these rules override that tool's default routing and advisory policy.

## Where evals go

- All stimuli for a plugin's skills, agents and commands go in **one** file: `plugins/<plugin-name>/evals/eval.yaml`. Don't write to the repository's top-level `evals/` folder.
- Fixtures go in `plugins/<plugin-name>/evals/fixtures/` and are staged with `agent_environment.files`.
- `agent_environment.skills` lists the plugin's skills as `../skills/<skill-name>`.
- Keep `defaults.executor: copilot-sdk`, `defaults.runs: 3` and `scoring.threshold: 0.7` unless the owner has a reason to change them.

## Minimums (CI enforces these)

- At least 10 stimuli, each with a unique `name`, a `prompt`, and at least one grader.
- At least 3 should-trigger stimuli using `skill-invocation` with `required`, and every skill in the plugin covered by one.
- At least 2 should-not-trigger stimuli using `skill-invocation` with `disallowed`.
- Task cases for real failure modes, plus stop and safety cases where the skill defines them.
- Tag every stimulus with `kind` (`trigger`, `no-trigger`, `task`, `stop`, `safety`) and `skill`.

## Advisory tags

Draft stimuli may be tagged `advisory: true` while being written. Before the pull request, the author reviews each one and removes the tag; CI warns on any that remain, and they don't count as reviewed.

## Expectations must be checkable

- Prefer deterministic graders: `skill-invocation`, `output-matches`, `output-contains`, `output-not-contains`, `diff-empty`, `file-exists`, `tool-calls`.
- Use a `prompt` judge with a `rubric` only for open-ended quality.
- Fixtures are small and fake: no real secrets, hostnames or customer data.

Lint before committing:

```bash
npx -y @microsoft/vally-cli@0.20.0 lint plugins --eval-spec plugins --strict
```
