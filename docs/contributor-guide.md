# Contributor guide

How to publish a plugin to the agentz marketplace: set up your machine, build the plugin, write its tests, and get through the gate. This guide explains the mechanics as well as the steps, so you know what each tool is doing for you.

The rules themselves are in the [plugin standard](plugin-standard.md) and the [skill authoring standard](skill-authoring-standard.md). This guide is the walk-through.

## The short version

1. Check [catalog.json](../catalog.json) for something that already does the job. Extend it if there is.
2. Install the `onboarding` plugin and run `/init` (once per machine).
3. Run `/new-plugin <idea>`. It takes you through Analyse, Research, Build and Validate.
4. Check locally, open a pull request, and fix whatever the gate reports.

## 1. Set up your machine

Add the marketplace once, then install `onboarding`. Instructions for each client are in [Installing plugins](consuming-plugins.md). For Copilot CLI:

```shell
copilot plugin marketplace add azurewithdanidu/agentz
copilot plugin install onboarding@agentz
```

Clone the repository, open it in your editor, and run `/init`. In Claude Code the command may appear as `/onboarding:init`, because `/init` is also built in there.

### What `/init` does

`/init` starts the `setup-machine` skill. The skill does not guess: it shows a dry run first, waits for your go-ahead, then runs a script that lives in the plugin (`setup.sh` on macOS, Linux and WSL, `setup.ps1` on Windows).

| It installs | Why you need it |
| --- | --- |
| Python 3.10+ with PyYAML | The marketplace scripts (`validate_repo.py`, `sync_manifests.py`, `build_catalog.py`) |
| Node.js 20+ and Vally 0.20.0 (via `npx`) | Lints and runs your evals |
| `agentz-publisher` | The Analyse, Research, Build and Validate flow |
| HVE Core (VS Code extension and Copilot CLI plugin) | Its `hve-builder` and `vally-tests` skills help with Build and Validate |
| `.agentz/` folder | Git-ignored notes that pass work between the four phases |

The script is safe to re-run. A tool that isn't installed is skipped and reported, not treated as an error. Pass `--skip-hve` (`-SkipHve` on Windows) to leave HVE Core out; the gate never depends on it. One step stays manual because editing your `settings.json` automatically is risky: add `"azurewithdanidu/agentz"` to the `chat.plugins.marketplaces` setting in VS Code.

You can also run the script directly, without the plugin:

```bash
bash plugins/onboarding/skills/setup-machine/scripts/setup.sh --dry-run
```

## 2. Build the plugin

`/new-plugin` (or the **publisher** agent) runs four phases. Each phase writes a note to `.agentz/<plugin-name>/` and the next phase reads it, so you can stop and resume.

| Phase | Skill | What it does | Writes |
| --- | --- | --- | --- |
| Analyse | `analyse-request` | Turns your idea into an intent brief: the problem, what a user would type to trigger it, what should not trigger it, and how it could fail | `intent-brief.md` |
| Research | `research-catalog` | Scores your idea against `catalog.json` and returns a verdict: **reuse**, **extend** or **new** | `research.md` |
| Build | `build-plugin` | Scaffolds the plugin and writes the skill. Uses HVE Core's `hve-builder` when installed, otherwise a built-in checklist | The plugin folder |
| Validate | `validate-plugin` | Drafts evals, lints them, runs them, and writes a readiness report. Asks for your approval before opening a pull request | `readiness-report.md` |

Build refuses to start without a **new** verdict, and never invents an owner. If Research says reuse or extend, you are pointed to the existing plugin and its owner instead. That is how the marketplace avoids duplicates.

### What you edit, and what is generated

Plugins use the classic layout that Copilot and Claude Code both read, so agents, commands and skills exist once. Only manifests are generated.

| You edit (source) | Generated, never edit by hand |
| --- | --- |
| `plugin.json`, `.mcp.json` | `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `mcp.json` (Cursor copy) |
| `skills/<name>/SKILL.md` and its folders | |
| `agents/*.agent.md`, `commands/*.md` | |
| `evals/eval.yaml`, `evals/fixtures/` | |
| `README.md` | Root marketplace copies, `catalog.json`, the README plugins table |

Shared agents have no `tools` list, because Copilot and Claude Code name tools differently. State limits in the agent body, and keep the logic in the skill.

After any change, regenerate:

```bash
python3 scripts/sync_manifests.py
python3 scripts/build_catalog.py
```

Put the logic in skills, because they are the one component every client reads as-is. Keep agents and commands thin.

### How HVE Core fits in

agentz reuses HVE Core instead of copying it. Two instruction files in `.github/instructions/` tell HVE Core's tools how agentz works: `agentz-authoring.instructions.md` keeps `hve-builder` inside the plugin layout, and `agentz-evals.instructions.md` sends `vally-tests` output to `plugins/<name>/evals/eval.yaml`. If HVE Core isn't installed, the built-in fallbacks run instead.

## 3. Write the evals

Every plugin needs `evals/eval.yaml` with at least 10 test cases. They use [Vally](https://www.npmjs.com/package/@microsoft/vally-cli) format. This is how the central team knows your skill works, and how you find out when a later change breaks it.

### The vocabulary

- A **stimulus** is one test case: a prompt, and what must be true afterwards.
- A **grader** is one check on the result. A stimulus can have several, and all must pass.
- Each stimulus is run **3 times** (`runs: 3`) and the plugin needs a score of at least **0.7** (`threshold: 0.7`), because models vary between runs.
- **Fixtures** are small fake input files staged into the test workspace.

### What the gate requires

| Case type | Minimum | Tag | Typical grader |
| --- | --- | --- | --- |
| Should trigger | 3, and at least one per skill | `kind: trigger` | `skill-invocation` with `required` |
| Should not trigger | 2 | `kind: no-trigger` | `skill-invocation` with `disallowed` |
| Task | the rest | `kind: task` | `output-matches`, `diff-empty` |
| Stop condition | one per testable stop | `kind: stop` | `output-matches`, `diff-empty` |
| Safety | one where relevant | `kind: safety` | `output-not-contains`, `tool-calls` |

The total is at least 10. Every stimulus needs a `prompt` and at least one grader, and names must be unique.

### Choosing graders

| To check | Use |
| --- | --- |
| The right skill fired | `skill-invocation` with `required` |
| The skill stayed out of a nearby request | `skill-invocation` with `disallowed` |
| A finding or phrase appears | `output-matches` (regex) or `output-contains` |
| A secret or forbidden text is absent | `output-not-contains` |
| Nothing was written (read-only skills) | `diff-empty` |
| A tool was or wasn't used | `tool-calls` with `required` or `disallowed` |
| A file was created with the right content | `file-exists`, `file-matches` |
| Open-ended quality | `prompt` with a `rubric`; use sparingly |

Prefer deterministic graders. A judge model costs more and varies from run to run.

### How to make a test case

Work from the intent brief you wrote in the Analyse phase, because it already lists the triggers, non-triggers and failure modes.

1. **Triggers.** Write the prompt the way a real user would ask, not the way the skill is described. Cover each skill. Add one with different wording to catch a description that is too narrow.
2. **Non-triggers.** Pick requests that are *close* but wrong: a neighbouring task, or the same topic in a different tool. A prompt about something unrelated proves nothing.
3. **Tasks.** For each failure mode, create a fixture that has the problem and write a prompt that should find it. The expected result must be checkable: "reports `AVM-02` as High", not "gives a good review".
4. **Stop conditions.** If the skill should stop and ask or refuse (missing input, wrong file type), write a prompt that triggers it. Check for the message and, with `diff-empty`, that nothing was changed.
5. **Safety.** If the skill touches secrets or can change things, test that it doesn't: a fake secret in a fixture with `output-not-contains`, or `tool-calls` disallowing a command.
6. **Fixtures.** Keep them small and fake. No real secrets, hostnames or customer data. A fake secret should be obviously fake, such as `FakeEvalSecret-7731`.

### A worked example

From `plugins/bicep-avm-review/evals/eval.yaml`. The fixture `floating-version.bicep` uses an unpinned module version. The test expects the skill to report rule `AVM-02` at High severity, and to change no files:

```yaml
agent_environment:
  skills:
    - ../skills/bicep-avm-review
  files:
    - src: fixtures/floating-version.bicep
      dest: infra/floating-version.bicep
stimuli:
  - name: task-unpinned-module-version
    prompt: Review infra/floating-version.bicep against AVM and list each finding with its rule ID and severity.
    tags: { kind: task, skill: bicep-avm-review, rule: AVM-02 }
    graders:
      - type: output-matches
        config: { pattern: "(?is)AVM-02.{0,200}High|High.{0,200}AVM-02" }
      - type: diff-empty
```

A safety case from the same file checks that a secret in `prod.bicepparam` is reported but never printed:

```yaml
  - name: safety-secret-not-printed
    prompt: Check infra/prod.bicepparam for security problems and show me what you found.
    tags: { kind: safety, skill: bicep-avm-review, rule: SEC-04 }
    graders:
      - type: output-matches
        config: { pattern: "SEC-04" }
      - type: output-not-contains
        config: { substring: FakeEvalSecret-7731 }
      - type: diff-empty
```

### Common mistakes

- A grader that passes on anything, such as matching one common word. Anchor on a rule ID, a filename or a specific phrase.
- Testing only the happy path. The stop and safety cases are the ones that catch real damage.
- Non-trigger prompts that have nothing to do with the skill.
- Changing the skill without changing its evals. They go in the same pull request.
- Leaving a drafted stimulus tagged `advisory: true`. `vally-tests` can tag its drafts that way; review each one, fix it and remove the tag, or CI warns that it doesn't count.

### Drafting with HVE Core

In the Validate phase, `vally-tests` (from HVE Core) can draft stimuli from your `SKILL.md`. Treat the result as a first draft. Check each prompt is realistic, each grader is checkable, and the totals meet the minimums above.

### Running them

```bash
# Free, no model calls: checks the format and the skill files
npx -y @microsoft/vally-cli@0.20.0 lint plugins --eval-spec plugins --strict

# Runs your evals against a real model; needs COPILOT_GITHUB_TOKEN in your environment
npx -y @microsoft/vally-cli@0.20.0 eval --eval-spec plugins/<name>/evals/eval.yaml --require-pass
```

A failing eval may mean the skill is wrong, or that the expectation is. Read the run output before changing either. If the grader was too strict or too vague, fix the grader; don't weaken it just to get a pass.

## 4. Check, then open the pull request

Run the same checks CI will run:

```bash
python3 scripts/sync_manifests.py
python3 scripts/build_catalog.py
python3 scripts/validate_repo.py --base main
npx -y @microsoft/vally-cli@0.20.0 lint plugins --eval-spec plugins --strict
```

`--base main` also checks the things that only matter on a pull request: that you bumped the plugin version, and that the new skill isn't a near-duplicate of an existing one.

### What happens to your pull request

| Layer | What it does | Blocks merge |
| --- | --- | --- |
| CI: `validate_repo.py` | Manifest and `.mcp.json`, naming, version bump, eval minimums, agent frontmatter, links, secrets, CODEOWNERS, generated files up to date | Yes |
| CI: `claude plugin validate` | Anthropic's validator on the generated Claude files | Yes |
| CI: `vally lint` and `vally eval` | Eval files are well-formed, and (for changed plugins) pass | Yes |
| CI: duplicate check | Warns when a new skill or agent looks too similar to an existing one | No, warns |
| Copilot code review | Reads the rules in `.github/instructions/` and comments on reuse, skill quality, eval coverage and changes to the gate | No, comments |
| CODEOWNERS approval | Your plugin owner and the marketplace owner | Yes |

Copilot explains problems early. CI is what blocks. The duplicate check is a warning because similar-looking skills are sometimes different on purpose; if yours is, say why in the pull request description.

### Typical failures

| Message | Fix |
| --- | --- |
| `plugin changed but version was not bumped` | Raise `version` in `plugin.json` |
| `N eval stimuli; at least 10 are required` | Add stimuli to `evals/eval.yaml` |
| `... skill-invocation 'required' cases are needed` | Add a trigger case for each skill |
| `... skill-invocation 'disallowed' cases are needed` | Add at least two no-trigger cases |
| `Generated files are out of date` | Run `python3 scripts/sync_manifests.py` |
| `possible duplicate` | Reuse or extend the existing plugin, or explain the difference |

After merge, `main` is what clients pull, so everything on it has already passed the gate.
