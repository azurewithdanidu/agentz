# agentz

Central agent-plugin marketplace by Azure with Danidu (`azurewithdanidu/agentz`). One repo, authored once, consumed by Claude Code, VS Code (Copilot), Copilot CLI and Cursor. It is also the live demo for a 1-hour talk on sharing agents and skills across an organisation without duplication, with proper quality gates.

## Golden rules

- `.claude-plugin/` files are the source of truth. Never hand-edit generated files: `.cursor-plugin/**`, `plugins/*/mcp.json`, `catalog.json`, and the plugins table in `README.md` (between the `plugins-table` markers).
- After changing any manifest, skill, agent or command, run:
  ```bash
  python3 scripts/sync_manifests.py
  python3 scripts/build_catalog.py
  python3 scripts/validate_repo.py            # add --base main for PR checks
  ```
- Every change to a plugin needs a semver bump in its `.claude-plugin/plugin.json`. CI fails otherwise.
- Put logic in skills (the only component portable everywhere). Keep agents, commands and hooks thin.
- No top-level `bin/` in a plugin (Claude org sync rejects it). Hooks go in `hooks/hooks.json`, not the plugin root.
- Write `source` paths as `./plugins/<name>`; folder name = plugin name = manifest name.

## Layout

- `.claude-plugin/marketplace.json`: the registry (marketplace name `agentz`)
- `plugins/<name>/`: one folder per plugin
  - `plugin-creator`: scaffolds new plugins (`scripts/scaffold.py`, `/new-plugin`)
  - `bicep-avm-review`: reference example of the skill structure
- `scripts/`: `sync_manifests.py`, `build_catalog.py`, `validate_repo.py`, `marketplace_lib.py` (needs PyYAML)
- `docs/`: `plugin-standard.md`, `skill-authoring-standard.md`, `consuming-plugins.md`
- `.github/`: `workflows/validate.yml`, `CODEOWNERS`, `copilot-instructions.md`, `instructions/plugin-review.instructions.md`, PR template

## The gate

- CI (`validate_repo.py`) blocks on: manifests, naming, version bump, at least 10 evals incl. trigger cases, broken links, secrets, CODEOWNERS, stale generated files.
- CI (`claude plugin validate .`) runs Anthropic's validator.
- Duplicate check: overlap coefficient on skill/agent names + descriptions vs base `catalog.json`; warns at >= 0.6. Calibrated on only a few skills; retune as the catalog grows.
- Copilot code review handles judgment calls (overlap, skill quality, eval quality, portability) via the instructions files. Deterministic checks stay in CI.

## Branches

- `chore/rename-to-agentz`: Contoso placeholders replaced with agentz values. Merge first.
- `demo/iac-checker`: deliberately failing PR for the talk (1 eval, no version bump, duplicate of `bicep-avm-review`). Keep open.
- `feature/iac-checker`: stale local branch from the first skeleton (Contoso names). Safe to delete.

## Verified platform facts (Nov 2026; recheck before slides)

- VS Code reads Claude-format plugins; marketplace via `chat.plugins.marketplaces` (Experimental), pin with `owner/repo#ref`.
- Copilot CLI: `copilot plugin marketplace add owner/repo`, `copilot plugin install name@marketplace`; reads `.claude-plugin/marketplace.json` as fallback (documented home is `.github/plugin/`).
- Cursor: `.cursor-plugin/plugin.json` + `.cursor-plugin/marketplace.json`, `mcp.json` (no dot); only `name` required; no `displayName` field. Team Marketplaces (Teams/Enterprise) via Dashboard > Plugins & MCPs > Import from Repo.
- Claude org sync: repo must be private/internal on github.com (GHES supported); 1,000 plugins per marketplace; follows the default branch, no pinning. This public repo cannot be org-synced.
- Claude marketplace supports `renames` (use for promotions/renames instead of breaking installs).
- Open Agent Plugins spec: root `plugin.json`; only skills and `mcp.json` are portable under it.

## Open work

1. Evals design: `evals/evals.yaml` format is a placeholder; the CI `evals` job is a stub. Only the count is enforced.
2. Enable Copilot code review automatically on PRs (repo rulesets) and confirm Actions run.
3. Test installs from each IDE before the talk.
4. Optional: a GitHub org to demo real team ownership in CODEOWNERS; a private copy to demo Claude org sync.

## Talk (1 hour) structure

Opening (problem: duplicated, unvetted agents/skills) -> Part 1 distribution: one central repo, any IDE, selective install (live demo) -> Part 2 plugin structure: anatomy, skill authoring flow, mandatory checklist, 10+ evals -> Part 3 central team gate: CI hard checks + Copilot review + duplicate check (live demo of failing vs passing PR) -> takeaways and Q&A.
