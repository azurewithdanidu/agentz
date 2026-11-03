## What this changes

<!-- New plugin, new skill, or change to an existing one? One or two sentences. -->

## Reuse check

- [ ] I searched `catalog.json` (or ran `research-catalog`) and nothing existing does this job, **or** I am extending the existing plugin: `<name>`
- [ ] Research verdict and readiness report (from `agentz-publisher`), if used: <!-- paste the summary -->

## Publishing checklist

- [ ] Ran `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`
- [ ] `python3 scripts/validate_repo.py` passes locally
- [ ] Version bumped in the plugin's root `plugin.json` (patch, minor or major)
- [ ] Vally evals in `evals/eval.yaml`: at least 10 stimuli, every skill has a should-trigger case, 2+ should-not-trigger cases
- [ ] `vally lint` passes and `vally eval` passes locally (no `advisory: true` tags left)
- [ ] Plugin README states owner, status, platforms and usage
- [ ] Tested in VS Code, plus any other client you target: <!-- Copilot CLI / Claude Code / Cursor -->
