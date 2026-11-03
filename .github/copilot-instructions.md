# Copilot instructions for agentz

agentz is a central marketplace of agent plugins. Plugins are authored in the open Agent Plugins 1.0 format, with VS Code and GitHub Copilot as the primary clients. Claude Code and Cursor files are generated from those sources by scripts.

## Your role on pull requests

You are the first reviewer of every plugin submission. Check the pull request against the rules in the path-specific files under `.github/instructions/`:

| File | Covers |
| --- | --- |
| `plugin-submission.instructions.md` | Every plugin PR: reuse, layout, ownership, versioning, README, secrets |
| `plugin-manifest.instructions.md` | `plugin.json`, `mcp.json`, marketplace registration |
| `plugin-skills.instructions.md` | Skill quality and structure |
| `plugin-agents.instructions.md` | Agents, commands, hooks, generated files |
| `plugin-evals.instructions.md` | Eval coverage and quality |
| `gate-changes.instructions.md` | Changes to CI, scripts, CODEOWNERS or these instructions |

## How to review

- Check every rule that applies to the changed files, including rules CI also enforces. CI is authoritative and blocks the merge; you are a second line that explains problems early and in plain language.
- Leave one comment per problem, on the line where it occurs. Say which rule it breaks and exactly what to change.
- Don't comment on things that follow the rules. Don't restate the diff.
- If you can't verify a rule from the diff (for example, whether evals pass), say what the author should confirm instead of assuming.
- When in doubt about a duplicate, raise it as a question, not a verdict.

## Source and generated files

Sources (edit these): each plugin's root `plugin.json`, `mcp.json`, `skills/`, `com.github.copilot/`, `evals/`, `README.md`, and the root `.claude-plugin/marketplace.json`.

Generated (never edited by hand): each plugin's `.claude-plugin/`, `.mcp.json`, `agents/`, `commands/`, `.cursor-plugin/`; at the root `.github/plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, `catalog.json`, and the plugins table in `README.md`. The fix for any of these is always: edit the source, then run `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`.
