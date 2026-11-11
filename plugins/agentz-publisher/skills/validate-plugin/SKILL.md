---
name: validate-plugin
description: Validate a new or changed agentz plugin before publishing by writing its Vally evals, running them, running the marketplace gate locally, and producing a publish-readiness report. Use when the user says "validate my plugin", "write evals for this skill", "is my plugin ready to publish", or after build-plugin finishes. This is phase 4 of 4 (Analyse, Research, Build, Validate). Do not use to review someone else's pull request.
---

# Validate before publishing

Runs the same checks as the marketplace CI gate, locally and before the pull request, so the PR arrives green. The central piece is the evals: at least 10 cases, each with a concrete input and a checkable expected result.

Opening the pull request changes an external system, so it needs the user's explicit approval.

## When to use

- After `build-plugin`, or after changing a plugin's skills.
- When someone asks whether their plugin is ready to publish.

## When not to use

- Reviewing a pull request someone else opened. CI and Copilot review do that.

## Inputs

- The plugin folder `plugins/<name>/`.
- `.agentz/<name>/intent-brief.md`: its trigger phrases, non-trigger cases and failure modes become evals.
- Node.js 20 or later for Vally. A GitHub Copilot sign-in to run evals (not needed for lint).

## Workflow

1. **Write the evals** in `plugins/<name>/evals/eval.yaml`, with fixtures in `plugins/<name>/evals/fixtures/`. Choose one:
   - **HVE Core installed:** run `vally-tests` in from-artifact mode with `files=plugins/<name>/skills/<skill>/SKILL.md`. The repository's `agentz-evals` instructions route it to the plugin's `eval.yaml`. Then remove any `advisory: true` tags it adds, after checking each case.
   - **Without HVE Core (always the case in Claude Code):** draft them by hand following the "Drafting stimuli by hand" steps in [references/eval-guide.md](references/eval-guide.md). This is a supported path, not a degraded one.

   Either way, cover every case in the brief and meet the minimums in the guide.
2. **Lint the evals** (no model calls):

   ```bash
   npx -y @microsoft/vally-cli@0.20.0 lint plugins/<name>/skills --eval-spec plugins/<name>/evals/eval.yaml
   ```

3. **Run the evals** (needs a Copilot sign-in):

   ```bash
   npx -y @microsoft/vally-cli@0.20.0 eval --eval-spec plugins/<name>/evals/eval.yaml --require-pass
   ```

   For each failing case, decide whether the skill or the eval is wrong. Fix the skill when the expectation is right. Never weaken an expectation just to pass.
4. **Run the gate:**

   ```bash
   python3 scripts/sync_manifests.py && python3 scripts/build_catalog.py
   python3 scripts/validate_repo.py --base origin/main
   ```

5. **Write the report** to `.agentz/<name>/readiness-report.md` using [templates/readiness-report.md](templates/readiness-report.md).
6. **Ask before opening the PR.** Show the report and ask the user to approve. Only then create a branch, commit and open the pull request, pasting the report's summary into the PR description.

## Stop conditions

- Fewer than 10 eval cases, or a skill with no trigger case: don't run step 3; finish the evals first.
- Any eval or gate check fails: don't open the PR. Report what failed.
- The user hasn't approved: don't push or open a PR.

## Output

- `plugins/<name>/evals/eval.yaml` and fixtures, a passing gate, and `.agentz/<name>/readiness-report.md`.
- **Done when:** evals pass, the gate passes, and the user has approved or declined the PR.
