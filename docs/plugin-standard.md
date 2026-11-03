# Plugin publishing standard

Every plugin in this marketplace is authored in the open [Agent Plugins 1.0](https://agent-plugins.org) format, with VS Code and GitHub Copilot as the primary clients. Claude Code and Cursor don't read that format yet (Cursor only partly), so their files are generated from it.

The easiest way to meet this standard is the `agentz-publisher` plugin, which walks you through four phases: Analyse, Research, Build and Validate. See [Building with HVE Core](#building-with-hve-core).

**Enforced by** says who checks each rule.

## Mandatory

| # | Requirement | Enforced by |
| --- | --- | --- |
| 1 | Folder at `plugins/<name>/`, registered in `.claude-plugin/marketplace.json` with `source: ./plugins/<name>` | CI |
| 2 | Name is lowercase-hyphenated, 64 characters or fewer, and the same in folder, manifest and marketplace entry | CI |
| 3 | Root `plugin.json` with the Agent Plugins `$schema`, name, semver version, description, and author name and email. No fields outside the spec | CI |
| 4 | Version bumped in `plugin.json` on every change (patch, minor or major) | CI (PRs) |
| 5 | At least one skill at `skills/<name>/SKILL.md`, frontmatter `name` matching the folder | CI |
| 6 | Skill description of 50 to 1,024 characters that says when to use it and when not to | CI and Copilot review |
| 7 | Vally evals in `evals/eval.yaml`: at least 10 stimuli, 3+ should-trigger (every skill covered), 2+ should-not-trigger, each with a prompt and graders | CI (`validate_repo.py`, `vally lint`) and Copilot review (quality) |
| 8 | Evals pass (3 runs, threshold 0.7) | CI on changed plugins, when the `COPILOT_GITHUB_TOKEN` secret is set |
| 9 | `README.md` with owner, status, platforms and usage | CI (exists) and Copilot review (content) |
| 10 | A CODEOWNERS line for `/plugins/<name>/` | CI |
| 11 | No secrets, keys or tokens in any file | CI |
| 12 | MCP servers in `mcp.json` with the Agent Plugins `$schema` and `type` of `stdio` or `streamable-http` | CI |
| 13 | Agents named `<name>.agent.md` with `name`, `description` and only mapped `tools` | CI |
| 14 | Generated files up to date (see below) | CI |
| 15 | No duplicate of an existing skill or agent, or a stated reason why it is different | CI warning, Copilot review, human approval |
| 16 | Follows the [skill authoring standard](skill-authoring-standard.md) | Copilot review and human approval |

## Layout

```text
plugins/<name>/
├── plugin.json                         # SOURCE: Agent Plugins 1.0 manifest
├── mcp.json                            # SOURCE (optional): Agent Plugins MCP servers
├── skills/<skill>/SKILL.md             # SOURCE: required; read as-is by every client
│   ├── steps/                          #   ordered procedures
│   ├── references/                     #   rules, mappings, schemas (one copy each)
│   ├── templates/                      #   output formats
│   └── scripts/                        #   deterministic checks
├── com.github.copilot/                 # SOURCE (optional): Copilot-specific components
│   ├── agents/<agent>.agent.md         #   custom agents
│   ├── commands/<command>.md           #   slash commands
│   └── hooks/hooks.json                #   hooks (avoid in shared plugins)
├── evals/eval.yaml                     # SOURCE: required; Vally evals, at least 10 stimuli
├── evals/fixtures/                     # SOURCE: small, fake input files for evals
├── README.md                           # SOURCE: required
│
├── .claude-plugin/plugin.json          # GENERATED for Claude Code
├── .mcp.json                           # GENERATED for Claude Code ("streamable-http" -> "http")
├── agents/<agent>.md                   # GENERATED for Claude Code (tools mapped)
├── commands/<command>.md               # GENERATED for Claude Code
└── .cursor-plugin/plugin.json          # GENERATED for Cursor
```

Run `python3 scripts/sync_manifests.py` after any change. Generated files carry a "GENERATED ... Do not edit" note where the format allows one.

## How each client reads a plugin

| Client | Reads | Gets |
| --- | --- | --- |
| VS Code (Copilot) | Root `plugin.json` with the Agent Plugins `$schema` | Skills, MCP, and everything in `com.github.copilot/` |
| Copilot CLI and the Copilot app | Root `plugin.json` (takes precedence over other manifests) | Skills, MCP, and everything in `com.github.copilot/` |
| Claude Code | `.claude-plugin/plugin.json` (ignores the root manifest and the Copilot namespace) | Skills, `.mcp.json`, generated `agents/` and `commands/` |
| Cursor | `.cursor-plugin/plugin.json` or the root `plugin.json` (precedence not documented) | At least skills and `mcp.json`. Agents and commands **to be confirmed** |

## Agent tools mapping

Copilot agents list tool sets. Claude agents are generated with the matching Claude tools:

| Copilot tool set | Claude Code tools |
| --- | --- |
| `read` | `Read` |
| `search` | `Grep`, `Glob` |
| `edit` | `Edit`, `Write` |
| `execute` | `Bash` |
| `web` | `WebFetch`, `WebSearch` |
| `todo` | `TodoWrite` |

Any other tool name fails CI. Extend `COPILOT_TO_CLAUDE_TOOLS` in `scripts/marketplace_lib.py` if you need one.

## Portability

| Component | Portable under Agent Plugins 1.0 | Guidance |
| --- | --- | --- |
| Skills | Yes | Put the logic here |
| MCP servers | Yes | One `mcp.json`; Claude's copy is generated |
| Agents | No (client namespace) | Keep thin; delegate to skills |
| Commands | No (client namespace) | Keep thin |
| Hooks | No (client namespace) | Avoid in shared plugins; not generated for Claude |

## Not allowed

- Hand-edited generated files.
- `agents/`, `commands/` or `.claude-plugin/` written by hand. Author them under `com.github.copilot/` and generate.
- A top-level `bin/` folder. Claude org sync rejects the plugin. Use `scripts/`.
- `hooks.json` at the plugin root, or a legacy `.plugin/` folder.

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

Set up a machine with `scripts/init.sh` (macOS, Linux, WSL) or `scripts/init.ps1` (Windows), or the `/agentz-init` command. Opening the repository in VS Code also recommends the HVE Core extension.
