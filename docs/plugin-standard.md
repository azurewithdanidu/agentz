# Plugin publishing standard

Every plugin in this marketplace uses the classic layout that VS Code (GitHub Copilot), Copilot CLI and Claude Code all read: a root `plugin.json`, `skills/`, `agents/`, `commands/` and `.mcp.json`. Each agent, command and skill exists once, so there is nothing to keep in sync by hand. Only the Claude Code and Cursor manifests are generated.

agentz deliberately does not use the [Agent Plugins 1.0](https://agent-plugins.org) packaging format. It is an open standard worth knowing, but only the Copilot clients read it, and it keeps agents and commands in a `com.github.copilot/` folder that Claude Code ignores. That would mean two copies of every agent. See [Why the classic layout](#why-the-classic-layout).

The easiest way to meet this standard is the `agentz-publisher` plugin, which walks you through four phases: Analyse, Research, Build and Validate. See [Building with HVE Core](#building-with-hve-core).

**Enforced by** says who checks each rule.

## Mandatory

| # | Requirement | Enforced by |
| --- | --- | --- |
| 1 | Folder at `plugins/<name>/`, registered in `.claude-plugin/marketplace.json` with `source: ./plugins/<name>` (or a pinned linked source; see [Linked plugins](#linked-plugins)) | CI |
| 2 | Name is lowercase-hyphenated, 64 characters or fewer, and the same in folder, manifest and marketplace entry | CI |
| 3 | Root `plugin.json` with name, semver version, description, and author name and email. No `$schema` and no `extensions` (they switch Copilot to Agent Plugins rules) | CI |
| 4 | Version bumped in `plugin.json` on every change (patch, minor or major) | CI (PRs) |
| 5 | At least one skill at `skills/<name>/SKILL.md`, frontmatter `name` matching the folder | CI |
| 6 | Skill description of 50 to 1,024 characters that says when to use it and when not to | CI and Copilot review |
| 7 | Vally evals in `evals/eval.yaml`: at least 10 stimuli, 3+ should-trigger (every skill covered), 2+ should-not-trigger, each with a prompt and graders | CI (`validate_repo.py`, `vally lint`) and Copilot review (quality) |
| 8 | Evals pass (3 runs, threshold 0.7) | CI on changed plugins, when the `COPILOT_GITHUB_TOKEN` secret is set |
| 9 | `README.md` with owner, status, platforms and usage | CI (exists) and Copilot review (content) |
| 10 | A CODEOWNERS line for `/plugins/<name>/` | CI |
| 11 | No secrets, keys or tokens in any file | CI |
| 12 | MCP servers in `.mcp.json` with `type` of `stdio` or `http` | CI |
| 13 | Agents at `agents/<name>.agent.md` with `name` and `description`, and no `tools` list | CI |
| 14 | Generated files up to date (see below) | CI |
| 15 | No duplicate of an existing skill or agent, or a stated reason why it is different | CI warning, Copilot review, human approval |
| 16 | Follows the [skill authoring standard](skill-authoring-standard.md) | Copilot review and human approval |

## Layout

```text
plugins/<name>/
├── plugin.json                         # SOURCE: manifest (no $schema, no extensions)
├── .mcp.json                           # SOURCE (optional): MCP servers
├── skills/<skill>/SKILL.md             # SOURCE: required; read as-is by every client
│   ├── steps/                          #   ordered procedures
│   ├── references/                     #   rules, mappings, schemas (one copy each)
│   ├── templates/                      #   output formats
│   └── scripts/                        #   deterministic checks
├── agents/<agent>.agent.md             # SOURCE (optional): read by Copilot and Claude Code
├── commands/<command>.md               # SOURCE (optional): slash commands
├── evals/eval.yaml                     # SOURCE: required; Vally evals, at least 10 stimuli
├── evals/fixtures/                     # SOURCE: small, fake input files for evals
├── README.md                           # SOURCE: required
│
├── .claude-plugin/plugin.json          # GENERATED for Claude Code
├── .cursor-plugin/plugin.json          # GENERATED for Cursor
└── mcp.json                            # GENERATED for Cursor (copy of .mcp.json)
```

Run `python3 scripts/sync_manifests.py` after any change.

### Linked plugins

A plugin can stay in its own repo and still be listed here. Run `/init` from the `onboarding` plugin in that repo. It adds an `agentz-sync` workflow, and each version bump on the default branch opens a draft pull request that:

- copies the source `plugin.json` and `README.md` into `plugins/<name>/`, which holds nothing else
- sets the registry `source` to `{"source": "github", "repo": "owner/repo", "sha": "<commit>"}`, plus `path` if the plugin isn't at the repo root

Clients install the skills, agents and commands from that commit. CI fetches the same commit and applies every content rule in the table above. When the commit changes, the version must be bumped. Fix any problem in the source repo and bump its version; the workflow updates the pull request.

Current limits:

- Public CI can't fetch a private source.
- The duplicate check doesn't cover a linked plugin's skills.
- VS Code and Cursor support for remote sources is not yet verified.

See [source repo setup](../plugins/onboarding/skills/sync-marketplace/references/setup.md).

## How each client reads a plugin

| Client | Reads | Gets |
| --- | --- | --- |
| VS Code (Copilot), Copilot CLI, Copilot app | Root `plugin.json` | Skills, `agents/`, `commands/`, `.mcp.json` |
| Claude Code | `.claude-plugin/plugin.json` (generated) | Skills, `agents/`, `commands/`, `.mcp.json` |
| Cursor | `.cursor-plugin/plugin.json` (generated) | Skills and `mcp.json`. Agents and commands **to be confirmed** |

## Agents

An agent file has to work in Copilot and in Claude Code, which use different tool names. So shared agents carry no `tools` list. Say what the agent must not do in its body (for example "You are read-only") and keep the logic in the skill.

## Why the classic layout

- One copy of each agent and command, readable by Copilot and Claude Code without generation.
- The Agent Plugins format puts agents in `com.github.copilot/`. Claude Code ignores that folder, so every agent would need a second, generated copy that can drift.
- A root `$schema` pointing at agent-plugins.org makes Copilot use Agent Plugins rules, which do not read a root `agents/` folder. That is why the gate forbids the `$schema`.
- The open format is still useful to know. Skills and MCP servers are portable under it, and agentz keeps them in the same places.

## Portability

| Component | Portable across clients | Guidance |
| --- | --- | --- |
| Skills | Yes | Put the logic here |
| MCP servers | Yes | One `.mcp.json`; Cursor's copy is generated |
| Agents | Copilot and Claude Code | Keep thin; delegate to skills; no `tools` list |
| Commands | Claude Code; Copilot **to be confirmed** | Keep thin |
| Hooks | No (formats differ) | Avoid in shared plugins |

## Not allowed

- Hand-edited generated files.
- `.claude-plugin/`, `.cursor-plugin/` or `mcp.json` written by hand. They are generated.
- A `com.github.copilot/` folder, or the Agent Plugins `$schema` or `extensions` in `plugin.json`.
- A `tools` list in a shared agent.
- A top-level `bin/` folder. Claude org sync rejects the plugin. Use `scripts/`.
- A legacy `.plugin/` folder.

## Versioning and lifecycle

- `0.x` means beta and `1.0.0` or later means stable. Promotion is a version bump, not a rename.
- To rename or retire a plugin, add it to the `renames` map in `.claude-plugin/marketplace.json` so existing Claude installs follow it.

## Building with HVE Core

[HVE Core](https://github.com/microsoft/hve-core) is Microsoft's framework for authoring agents and skills. agentz uses it as the build framework and adds the marketplace layer on top. HVE Core is optional: the gate doesn't depend on it, so anyone who meets the standard can publish.

| Phase | Tool | What it adds |
| --- | --- | --- |
| Analyse | `agentz-publisher` / `analyse-request` | Intent brief: problem, triggers, non-triggers, failure modes |
| Research | `agentz-publisher` / `research-catalog` | Reuse, extend or new verdict against `catalog.json` (also used during HVE `rpi-research`) |
| Build | HVE Core `hve-builder` (via `build-plugin`) | Authoring against HVE's requirements catalog, with an independent reviewer |
| Validate | HVE Core `vally-tests` + Vally (via `validate-plugin`) | Evals drafted from the skill, linted and run before the PR |

Two instruction files make HVE Core work inside agentz without changing it: `.github/instructions/agentz-authoring.instructions.md` keeps `hve-builder` in the plugin layout, and `.github/instructions/agentz-evals.instructions.md` routes `vally-tests` output to `plugins/<name>/evals/eval.yaml`.

Set up a machine with the `onboarding` plugin: install it and run `/init`. The script behind it is `plugins/onboarding/skills/setup-machine/scripts/setup.sh` (macOS, Linux, WSL) or `setup.ps1` (Windows). HVE Core is a plugin: `/init` installs it for Copilot CLI and prints the manual VS Code step; in Claude Code it is reported as skipped and the built-in fallbacks are used.
