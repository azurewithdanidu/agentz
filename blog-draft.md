---
title: "One Repo, Every IDE: Building a Central Agent Marketplace Without the Duplicates"
description: "How I built agentz, a central agent-plugin marketplace that VS Code, Copilot CLI, Claude Code and Cursor all install from, with a quality gate that actually blocks bad submissions"
author: Danidu Weerasinghe (Azure with Danidu)
ms.date: 2026-11-12
ms.topic: concept
keywords:
  - github copilot
  - claude code
  - agent plugins
  - skills
  - ai governance
  - platform engineering
estimated_reading_time: 12
---

<!-- markdownlint-disable-file -->

<!--
  DRAFT for the blogger agent to refine.
  Source repo: https://github.com/azurewithdanidu/agentz
  Related talk: "One Repo, Every IDE: Sharing Agents and Skills Across Your Organisation Without the Duplicates"
  Tone target: first person, practical, honest about what broke along the way.
  TODO markers below flag places that need screenshots, links or numbers before publishing.
-->

## The problem: ten teams, ten versions of the same skill

Ask any engineering organisation that has adopted GitHub Copilot or Claude Code how many "review my Bicep" prompts exist across their teams. The honest answer is usually "we have no idea, but more than one".

Every team writes its own agents, skills and prompts. The copies drift apart within weeks. Nobody knows which version is current, nobody owns them, nothing is tested, and nothing is reviewed. The real cost isn't storage, it's trust:

* Wasted effort rebuilding what already exists.
* Uneven quality: some skills trigger reliably, some never fire at all.
* Security risk: a shared skill runs with the user's permissions, so an unreviewed one is a supply-chain risk, the same as an unreviewed package.

I wanted to fix this properly, so I built [agentz](https://github.com/azurewithdanidu/agentz): one central GitHub repo that acts as an agent-plugin marketplace for VS Code, Copilot CLI, Claude Code and Cursor, with a quality gate that every submission has to pass. This post walks through how it works and what I learned building it.

## The idea: a GitHub repo is the marketplace

There's no npm package, no internal registry service, no copies per tool. A plain GitHub repo is the marketplace:

* `.claude-plugin/marketplace.json` is the registry source (Claude Code requires this exact file).
* `plugins/<name>/` holds one folder per plugin.
* Each client installs directly from the repo.

Installing looks like this:

```bash
# Copilot CLI
copilot plugin marketplace add azurewithdanidu/agentz
copilot plugin install bicep-avm-review@agentz
```

In VS Code, you add the repo via the `chat.plugins.marketplaces` setting (experimental at the time of writing), and you can pin with `owner/repo#ref`. Claude Code and Cursor have their own marketplace mechanisms that read generated copies of the same registry.

The point is selective install: a team browses the catalog, installs the one plugin they need, and ignores the rest. No forking, no copy-paste.

## One plugin, read four ways

The interesting engineering problem is that every client reads a plugin differently. Here's who reads what:

| Client      | Reads                                     | Gets                                    |
|-------------|-------------------------------------------|-----------------------------------------|
| VS Code     | root `plugin.json`                        | skills, MCP, agents, commands           |
| Copilot CLI | root `plugin.json`                        | skills, MCP, agents, commands           |
| Claude Code | `.claude-plugin/plugin.json` (generated)  | skills, MCP, agents, commands           |
| Cursor      | `.cursor-plugin/plugin.json` (generated)  | skills, MCP (agents still to confirm)   |

The layout that makes this work is the classic plugin layout: a root `plugin.json`, plus `agents/`, `commands/`, `skills/` and `.mcp.json` folders that VS Code, Copilot CLI and Claude Code all read directly. Each artifact exists exactly once. Only the manifests for Claude Code and Cursor are generated.

```text
plugins/bicep-avm-review/
  plugin.json          <- source: name, version, description
  .mcp.json            <- source: MCP servers (type: http or stdio)
  agents/              <- source: one .agent.md per agent
  skills/              <- source: the actual logic
  evals/               <- source: Vally eval spec + fixtures
  README.md            <- source: owner, status, usage
  .claude-plugin/      <- GENERATED, never hand-edited
  .cursor-plugin/      <- GENERATED
  mcp.json             <- GENERATED (Cursor copy of .mcp.json)
```

### The detour I had to undo

I originally converted everything to the Agent Plugins 1.0 open format (GA in August 2026 for VS Code, Copilot CLI and the Copilot app). It's a genuinely good spec, published with AWS, Anysphere, Microsoft, OpenAI and Vercel on board. But it keeps agents and commands inside a `com.github.copilot/` namespace folder that only the Copilot clients read. Claude Code (Anthropic isn't on the steering committee) ignores both the root manifest and the namespace folder, which would have forced a generated second copy of every agent and command. Generated copies of manifests are fine; generated copies of behavioural content drift, and drift is the exact problem I set out to kill.

Worse, a root `$schema` pointing at the Agent Plugins spec switches Copilot into Agent Plugins semantics, where it stops reading the root `agents/` folder entirely. So in this repo, that `$schema` is forbidden and CI fails on it. The classic layout won: one copy of everything, read natively by the clients that matter most, with generation reserved for manifests only.

<!-- TODO: link to the Agent Plugins spec and the GA announcement -->

## Author once, generate the rest

Hand-maintained mirrors drift on day one, so everything derived is scripted:

```bash
python3 scripts/sync_manifests.py   # Claude + Cursor manifests, marketplace copies
python3 scripts/build_catalog.py    # catalog.json + README plugins table
python3 scripts/validate_repo.py    # the full gate, locally
```

CI fails the build if any generated file is stale or hand-edited. The fix is always the same: edit the source, re-run the scripts.

`catalog.json` deserves a special mention. It indexes every plugin, skill, agent and command in the repo, regenerated on every change, and it's searchable by both people and tools. The scaffolding skill checks it before creating anything new, because the cheapest duplicate is the one that never gets written.

## Skills carry the logic; agents stay thin

The single most important design rule: put the logic in skills, because skills are the only component every client loads. Agents and commands are thin wrappers that find inputs and hand off to a skill. If your logic lives in an agent file, it works in one tool and nowhere else.

Shared agents in agentz have only `name` and `description` in their frontmatter. No `tools` list, because Copilot and Claude Code name their tools differently; any limits (such as read-only behaviour) are stated in the agent body in plain language.

The second most important rule: the skill description decides whether a skill ever fires. Compare:

* Weak: "Helps with Bicep."
* Strong: "Review Bicep templates against Azure Verified Modules. Use when the user asks to review my Bicep, check AVM compliance, or audit a template. Do not use for Terraform or for deploying."

What it does, when to use it with real user phrasings, and when not to. That one sentence pattern is the biggest triggering factor I've found.

Skills follow progressive loading: `SKILL.md` is a short entry point and workflow, while `steps/`, `references/`, `templates/` and `scripts/` hold the detail that gets loaded only when needed. One copy of every rule, linked, never repeated.

## The publishing flow: Analyse, Research, Build, Validate

Contributing a plugin isn't a free-for-all. The repo ships its own publishing framework as a plugin (`agentz-publisher`), which walks a contributor through four phases:

1. Analyse the request: what should this plugin actually do?
2. Research the catalog: does something like it already exist? (A script searches `catalog.json` before anything is scaffolded.)
3. Build the plugin: scaffold the structure, write the skill, keep agents thin.
4. Validate: run the local checks and the eval suite before opening a PR.

Build and Validate integrate with HVE Core's `hve-builder` and `vally-tests` agents when they're installed, with built-in fallbacks when they're not. The gate itself never depends on HVE Core, so a contributor on Claude Code (where HVE Core isn't supported) gets a first-class path too.

There's also an `onboarding` plugin with an `/init` command that sets up a contributor machine: the publisher plugin, HVE Core, Python and Vally, detecting which clients are installed and configuring only those.

## Evals: ten or more, or it doesn't merge

Every plugin ships a Vally eval spec (`evals/eval.yaml`). The minimums are enforced by CI:

* 10+ stimuli overall.
* 3+ skill-invocation cases, covering every skill in the plugin, written as real user phrasings.
* 2+ disallowed cases: nearby requests that should *not* trigger the skill.
* Fixtures must exist for every case that references one.

Evals that only restate the happy path prove nothing. The should-not-trigger cases are what catch over-eager descriptions, and the task cases cover the failure modes that actually matter. CI runs `vally lint` on every PR with no model calls, and runs the full `vally eval --require-pass` against a real model when the token secret is present.

<!-- TODO: add a short excerpt from a real eval.yaml, e.g. bicep-avm-review -->

## The gate: CI decides, Copilot explains, people approve

This is the part I'd argue matters most for any organisation doing this for real. The gate has three layers, and each one does what it's actually good at:

| Layer               | Role                                            |
|---------------------|-------------------------------------------------|
| CI (`validate_repo.py` + Anthropic's validator) | Pass/fail rules; blocks the merge |
| Copilot code review | Explains problems early, in plain language; flags judgment calls |
| CODEOWNERS          | The owning team approves; humans have the last word |

CI checks the manifest rules (no forbidden `$schema`, no `extensions`, no namespace folder), `.mcp.json` shape, agent frontmatter, naming, a semver bump on every plugin change, the eval minimums, broken links, secrets, CODEOWNERS entries, and stale generated files. Copilot can't block a merge, so anything pass/fail belongs in CI where it can't be talked around.

Copilot reviews against small, path-specific instruction files in `.github/instructions/`: one for submissions, one for manifests, one for skills, one for agents, one for evals. It leaves one inline comment per problem, naming the rule and the exact fix, plus a structured review summary with a verdict.

### The loophole worth knowing about

Copilot reads its review instructions from the PR's branch. That means a malicious (or merely careless) PR can rewrite its own review rules. Defence in depth handles it: a dedicated `gate-changes` instruction file flags any PR that touches `.github/` or `scripts/`, and CODEOWNERS forces the marketplace owner to approve those changes. The weak point is caught by a rule *and* by a human.

### Catching duplicates automatically

New skill descriptions are compared against the catalog using an overlap coefficient, warning at 0.6 or above. My first attempt used Jaccard similarity and missed an obvious duplicate at 0.38; the overlap coefficient catches a short description contained inside a longer one. In the demo case, the duplicate scores 0.87 against the existing skill while the next closest scores 0.20. Importantly, it warns rather than blocks: a human decides whether it's really a duplicate.

<!-- TODO: screenshot of the failing demo PR (iac-checker) with CI annotations and Copilot comments -->

## Lesson learned: verify the platform, not the blog post

Before building any of this, I fact-checked 16 claims from my starting research against the actual tools. Seven were confirmed, five were partly right, and four were flat wrong. Examples of wrong claims I almost repeated: that GitHub Enterprise Server was unsupported for Claude org sync (it is supported), that there's a 500-plugin cap (it's 1,000), and that no client supports pinning (VS Code and Copilot CLI both can).

These tools change monthly. If you're building on them, test the actual behaviour in the actual client before you commit to an architecture, and expect to re-verify before you present or publish anything.

## Takeaways

* One repo, every IDE: author each skill, agent and command once in a layout the clients read natively, and generate only manifests.
* One standard: every plugin has an owner, a semver version, a README and 10+ evals, and the standard says who enforces each rule.
* One gate: CI decides, Copilot explains, people approve. Hard rules go where they can't be negotiated with.

The repo is public at [github.com/azurewithdanidu/agentz](https://github.com/azurewithdanidu/agentz) if you want to poke at the scripts, the instruction files or the eval specs. The gate scripts in particular (`scripts/validate_repo.py`, `scripts/sync_manifests.py`, `scripts/build_catalog.py`) are small enough to read in one sitting and adapt to your own organisation.

<!-- TODO before publishing:
  - Add hero image / diagram of the three-layer gate
  - Confirm current client install instructions (they change often)
  - Link the talk recording if/when available
  - Decide on canonical post URL and cross-post plan
-->
