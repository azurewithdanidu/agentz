# agentz

Central agent-plugin marketplace by Azure with Danidu (`azurewithdanidu/agentz`). One repo using the classic plugin layout that Copilot and Claude Code both read (each skill, agent and command exists once), consumed by VS Code (Copilot, primary), Copilot CLI, Claude Code and Cursor. It is also the live demo for a 1-hour talk on sharing agents and skills across an organisation without duplication, with proper quality gates.

## Golden rules

- Plugins use the classic layout (not the Agent Plugins 1.0 format; see "Why classic" below). Per plugin, edit only: root `plugin.json` (no `$schema`, no `extensions`), `.mcp.json`, `skills/`, `agents/<name>.agent.md`, `commands/<name>.md`, `evals/`, `README.md`.
- Never hand-edit generated files. Per plugin: `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `mcp.json` (Cursor copy of `.mcp.json`). At the root: `.github/plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, `catalog.json`, and the plugins table in `README.md`.
- The registry source is `.claude-plugin/marketplace.json` (Claude needs this file; the Copilot and Cursor copies are generated).
- After changing any manifest, skill, agent or command, run:
  ```bash
  python3 scripts/sync_manifests.py
  python3 scripts/build_catalog.py
  python3 scripts/validate_repo.py            # add --base main for PR checks
  ```
- Every change to a plugin needs a semver bump in its root `plugin.json`. CI fails otherwise.
- Shared agents have `name` and `description` only. No `tools` list: Copilot and Claude Code name tools differently. State limits (for example read-only) in the body.
- `.mcp.json` uses `type: http` (or `stdio`).
- Never add a `com.github.copilot/` folder or an Agent Plugins `$schema`: the `$schema` switches Copilot to rules that ignore the root `agents/` folder. CI fails on both.
- Put logic in skills (the only component portable everywhere). Keep agents, commands and hooks thin.
- No top-level `bin/` in a plugin (Claude org sync rejects it). Avoid hooks in shared plugins; the formats differ between clients.
- Write `source` paths as `./plugins/<name>`; folder name = plugin name = manifest name.

## Layout

- `.claude-plugin/marketplace.json`: the registry (marketplace name `agentz`); `.github/plugin/marketplace.json` and `.cursor-plugin/marketplace.json` are generated copies
- `plugins/<name>/`: one folder per plugin
  - `agentz-publisher` (replaces `plugin-creator`, mapped in marketplace `renames`): the four-phase publishing flow. Skills `analyse-request`, `research-catalog`, `build-plugin`, `validate-plugin`; agent `publisher`; commands `/new-plugin`; `scripts/scaffold.py`; `skills/research-catalog/scripts/search_catalog.py`
  - `onboarding`: `/init` contributor machine setup: agentz-publisher, HVE Core, Python, Vally (skill `setup-machine`)
  - `bicep-avm-review`: reference example of the skill structure
- `scripts/`: `sync_manifests.py`, `build_catalog.py`, `validate_repo.py`, `marketplace_lib.py` (needs PyYAML)
- `docs/`: `contributor-guide.md` (setup, the four phases, writing evals, the PR gate), `plugin-standard.md`, `skill-authoring-standard.md`, `consuming-plugins.md`
- `.github/`: `workflows/validate.yml`, `CODEOWNERS`, `copilot-instructions.md`, `instructions/*.instructions.md` (Copilot PR review rules, split by path), PR template

## Publishing framework (Analyse, Research, Build, Validate)

- Analyse and Research are agentz's own (`agentz-publisher`); Build and Validate use HVE Core (`hve-builder`, `vally-tests`) when installed, with fallbacks when not. The gate never depends on HVE Core.
- HVE Core integration is by host-extension instructions only: `.github/instructions/agentz-authoring.instructions.md` and `agentz-evals.instructions.md`. Don't copy HVE Core content into the repo.
- Handoff notes live in `.agentz/<plugin>/` (git-ignored): `intent-brief.md`, `research.md`, `readiness-report.md`.
- Machine setup is the `onboarding` plugin: `/init` runs skill `setup-machine`, which wraps `skills/setup-machine/scripts/setup.sh` / `setup.ps1` (`--skip-hve`, `--hve-ref`, `--dry-run`; contributors only). `/init` is also a built-in in Claude Code, so it may show as `/onboarding:init` there (untested). `.vscode/extensions.json` recommends the HVE Core extension (`ise-hve-essentials.hve-core`).

## The gate

- CI (`validate_repo.py`) blocks on: manifest (no Agent Plugins `$schema`/`extensions`, no `com.github.copilot/`), `.mcp.json`, agent frontmatter (no `tools`), naming, version bump, Vally eval minimums (below), broken links, secrets, CODEOWNERS, stale generated files.
- CI (`claude plugin validate .`, pinned 2.1.317) runs Anthropic's validator.
- CI `eval-lint` runs `vally lint plugins --eval-spec plugins --strict` (Vally 0.20.0, no model calls). CI `evals` runs `vally eval --require-pass` for changed plugins when the `COPILOT_GITHUB_TOKEN` secret exists, otherwise warns.
- Eval minimums: 10+ stimuli, 3+ `skill-invocation` required (every skill covered), 2+ disallowed; fixtures must exist.
- Duplicate check: overlap coefficient on skill/agent names + descriptions vs base `catalog.json`; warns at >= 0.6. Calibrated on only a few skills; retune as the catalog grows.
- Copilot code review checks every rule (submission, manifest, skills, agents, evals, gate changes) via `.github/copilot-instructions.md` and path-specific files in `.github/instructions/`. CI stays authoritative and blocks merges; Copilot explains problems early. Copilot reads instructions from the PR branch, so `gate-changes.instructions.md` flags any PR that weakens the gate.

## Branches

- `main` has everything merged so far: the rename, the Agent Plugins conversion, the publisher and the onboarding plugin.
- `fix/classic-layout`: moves every plugin from the Agent Plugins 1.0 layout back to the classic layout (one copy of each agent and command). Merge first.
- `demo/iac-checker`: deliberately failing PR for the talk (too few evals, no version bump, duplicate of `bicep-avm-review`). Keep open; rebase onto `main` after `fix/classic-layout`.
- `demo/essay-writer`: a passing PR for the talk. Rebase onto `main` after `fix/classic-layout` and convert to the classic layout.
- Stale local branches (`feature/iac-checker`, `demo/iac-checker-old`) are safe to delete.

## Why classic (not Agent Plugins 1.0)

Agent Plugins 1.0 keeps agents and commands in `com.github.copilot/`, which only the Copilot clients read. Claude Code would need a generated second copy of every agent and command, which can drift. The classic layout (root `agents/`, `commands/`, `skills/`, `.mcp.json`) is read by Copilot and Claude Code directly. A root `$schema` pointing at agent-plugins.org switches Copilot to Agent Plugins rules, so it is forbidden. We still talk about the open format in the talk; skills and MCP servers are portable under both.

Still to verify in real clients: Cursor loading `agents/` and `commands/`; Copilot loading `commands/` (it may want `prompts/`); one agent file working in both clients without a `tools` list.

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
