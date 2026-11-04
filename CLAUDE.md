# agentz

Central agent-plugin marketplace by Azure with Danidu (`azurewithdanidu/agentz`). One repo, authored once in the open **Agent Plugins 1.0** format (https://agent-plugins.org), consumed by VS Code (Copilot, primary), Copilot CLI, Claude Code and Cursor. It is also the live demo for a 1-hour talk on sharing agents and skills across an organisation without duplication, with proper quality gates.

## Golden rules

- Plugins are authored in Agent Plugins 1.0. Per plugin, edit only: root `plugin.json` (with the Agent Plugins `$schema`), `mcp.json`, `skills/`, `com.github.copilot/` (agents as `<name>.agent.md`, commands), `evals/`, `README.md`.
- Never hand-edit generated files. Per plugin: `.claude-plugin/plugin.json`, `.mcp.json`, `agents/`, `commands/`, `.cursor-plugin/plugin.json`. At the root: `.github/plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, `catalog.json`, and the plugins table in `README.md`.
- The registry source is still `.claude-plugin/marketplace.json` (the spec defines no marketplace format, and Claude needs this file).
- After changing any manifest, skill, agent or command, run:
  ```bash
  python3 scripts/sync_manifests.py
  python3 scripts/build_catalog.py
  python3 scripts/validate_repo.py            # add --base main for PR checks
  ```
- Every change to a plugin needs a semver bump in its root `plugin.json`. CI fails otherwise.
- Agent `tools` must use Copilot tool sets that map to Claude (`read`, `search`, `edit`, `execute`, `web`, `todo`); the mapping lives in `COPILOT_TO_CLAUDE_TOOLS` in `scripts/marketplace_lib.py`.
- `mcp.json` uses `type: streamable-http` (or `stdio`); the generator converts it to Claude's `http`.
- Put logic in skills (the only component portable everywhere). Keep agents, commands and hooks thin.
- No top-level `bin/` in a plugin (Claude org sync rejects it). Hooks go in `com.github.copilot/hooks/hooks.json` (avoid in shared plugins; not generated for Claude).
- Write `source` paths as `./plugins/<name>`; folder name = plugin name = manifest name.

## Layout

- `.claude-plugin/marketplace.json`: the registry (marketplace name `agentz`); `.github/plugin/marketplace.json` and `.cursor-plugin/marketplace.json` are generated copies
- `plugins/<name>/`: one folder per plugin
  - `agentz-publisher` (replaces `plugin-creator`, mapped in marketplace `renames`): the four-phase publishing flow. Skills `analyse-request`, `research-catalog`, `build-plugin`, `validate-plugin`; agent `publisher`; commands `/new-plugin`; `scripts/scaffold.py`; `skills/research-catalog/scripts/search_catalog.py`
  - `onboarding`: `/init` contributor machine setup: agentz-publisher, HVE Core, Python, Vally (skill `setup-machine`)
  - `bicep-avm-review`: reference example of the skill structure
- `scripts/`: `sync_manifests.py`, `build_catalog.py`, `validate_repo.py`, `marketplace_lib.py` (needs PyYAML)
- `docs/`: `plugin-standard.md`, `skill-authoring-standard.md`, `consuming-plugins.md`
- `.github/`: `workflows/validate.yml`, `CODEOWNERS`, `copilot-instructions.md`, `instructions/*.instructions.md` (Copilot PR review rules, split by path), PR template

## Publishing framework (Analyse, Research, Build, Validate)

- Analyse and Research are agentz's own (`agentz-publisher`); Build and Validate use HVE Core (`hve-builder`, `vally-tests`) when installed, with fallbacks when not. The gate never depends on HVE Core.
- HVE Core integration is by host-extension instructions only: `.github/instructions/agentz-authoring.instructions.md` and `agentz-evals.instructions.md`. Don't copy HVE Core content into the repo.
- Handoff notes live in `.agentz/<plugin>/` (git-ignored): `intent-brief.md`, `research.md`, `readiness-report.md`.
- Machine setup is the `onboarding` plugin: `/init` runs skill `setup-machine`, which wraps `skills/setup-machine/scripts/setup.sh` / `setup.ps1` (`--skip-hve`, `--hve-ref`, `--dry-run`; contributors only). `/init` is also a built-in in Claude Code, so it may show as `/onboarding:init` there (untested). `.vscode/extensions.json` recommends the HVE Core extension (`ise-hve-essentials.hve-core`).

## The gate

- CI (`validate_repo.py`) blocks on: Agent Plugins manifest and `mcp.json` schema, agent tool mapping, naming, version bump, Vally eval minimums (below), broken links, secrets, CODEOWNERS, stale generated files.
- CI (`claude plugin validate .`, pinned 2.1.317) runs Anthropic's validator.
- CI `eval-lint` runs `vally lint plugins --eval-spec plugins --strict` (Vally 0.20.0, no model calls). CI `evals` runs `vally eval --require-pass` for changed plugins when the `COPILOT_GITHUB_TOKEN` secret exists, otherwise warns.
- Eval minimums: 10+ stimuli, 3+ `skill-invocation` required (every skill covered), 2+ disallowed; fixtures must exist.
- Duplicate check: overlap coefficient on skill/agent names + descriptions vs base `catalog.json`; warns at >= 0.6. Calibrated on only a few skills; retune as the catalog grows.
- Copilot code review checks every rule (submission, manifest, skills, agents, evals, gate changes) via `.github/copilot-instructions.md` and path-specific files in `.github/instructions/`. CI stays authoritative and blocks merges; Copilot explains problems early. Copilot reads instructions from the PR branch, so `gate-changes.instructions.md` flags any PR that weakens the gate.

## Branches

- `chore/rename-to-agentz`: Contoso placeholders replaced with agentz values. Merge first.
- `feat/agent-plugins-spec`: converts every plugin to Agent Plugins 1.0 with generated Claude/Cursor files. Merge second.
- `feat/hve-publisher`: agentz-publisher (Analyse, Research, Build, Validate), HVE Core host-extension instructions, Vally evals and CI, contributor init. Merge third.
- `feat/onboarding`: the `onboarding` plugin (moves machine setup out of `scripts/` and `agentz-publisher`). Merge fourth, after `feat/hve-publisher`.
- `demo/iac-checker`: deliberately failing PR for the talk (too few evals, no version bump, duplicate of `bicep-avm-review`), rebuilt on top of `feat/hve-publisher`. Keep open.
- `feature/iac-checker`: stale local branch from the first skeleton (Contoso names). Safe to delete.

## Verified platform facts (Nov 2026; recheck before slides)

- Agent Plugins 1.0 GA (Aug 2026) in VS Code, Copilot CLI and the Copilot app. A root `plugin.json` with the canonical `$schema` gets Agent Plugins semantics in VS Code and takes precedence in Copilot CLI. Copilot-specific agents/commands/rules/hooks load from `com.github.copilot/`. Only skills and `mcp.json` are portable. The manifest schema is closed.
- Claude Code does not support Agent Plugins (Anthropic not on the steering committee); it reads `.claude-plugin/plugin.json` and ignores the root manifest and namespace folder (verified with `claude plugin validate`).
- VS Code marketplace via `chat.plugins.marketplaces` (Experimental), pin with `owner/repo#ref`.
- Copilot CLI: `copilot plugin marketplace add owner/repo`, `copilot plugin install name@marketplace`; documented marketplace home is `.github/plugin/marketplace.json` (generated here); `.claude-plugin/marketplace.json` is a fallback.
- Cursor: `.cursor-plugin/plugin.json` + `.cursor-plugin/marketplace.json`, `mcp.json` (no dot); only `name` required; no `displayName` field. Precedence between root `plugin.json` and `.cursor-plugin/plugin.json` is undocumented; under Agent Plugins semantics Cursor loads skills + MCP only. Team Marketplaces (Teams/Enterprise) via Dashboard > Plugins & MCPs > Import from Repo.
- Claude org sync: repo must be private/internal on github.com (GHES supported); 1,000 plugins per marketplace; follows the default branch, no pinning. This public repo cannot be org-synced.
- Claude marketplace supports `renames` (use for promotions/renames instead of breaking installs).

## Open work

1. Evals are Vally specs (`plugins/<name>/evals/eval.yaml`) and lint cleanly, but haven't been run against a real model yet. Add the `COPILOT_GITHUB_TOKEN` secret and run them; tune expectations that fail for the wrong reason.
1a. Test the HVE Core integration in VS Code: does `hve-builder` stay in the plugin layout, and does `vally-tests` write to the plugin's `eval.yaml`, as the agentz instructions ask?
2. Enable Copilot code review automatically on PRs (repo rulesets) and confirm Actions run.
3. Test installs from each client before the talk, especially whether Cursor shows agents/commands.
4. Optional: a GitHub org to demo real team ownership in CODEOWNERS; a private copy to demo Claude org sync.

## Talk (1 hour) structure

Opening (problem: duplicated, unvetted agents/skills) -> Part 1 distribution: one central repo, any IDE, selective install (live demo) -> Part 2 plugin structure: anatomy, skill authoring flow, mandatory checklist, 10+ evals -> Part 3 central team gate: CI hard checks + Copilot review + duplicate check (live demo of failing vs passing PR) -> takeaways and Q&A.
