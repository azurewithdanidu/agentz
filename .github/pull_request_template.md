## What this changes

<!-- New plugin, new skill, or change to an existing one? One or two sentences. -->

## Reuse check

- [ ] I searched `catalog.json` and nothing existing does this job, **or** I am extending the existing plugin: `<name>`

## Publishing checklist

- [ ] Ran `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`
- [ ] `python3 scripts/validate_repo.py` passes locally
- [ ] Version bumped in the plugin's root `plugin.json` (patch, minor or major)
- [ ] At least 10 evals, including trigger cases that should and should not fire
- [ ] Evals run locally and pass
- [ ] Plugin README states owner, status, platforms and usage
- [ ] Tested in VS Code, plus any other client you target: <!-- Copilot CLI / Claude Code / Cursor -->
