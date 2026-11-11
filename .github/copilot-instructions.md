# Copilot instructions for agentz

agentz is a central marketplace of agent plugins. Plugins use the classic layout that VS Code, GitHub Copilot and Claude Code all read (root `plugin.json`, `agents/`, `commands/`, `skills/`, `.mcp.json`), so each artifact exists once. Only manifests are generated for Claude Code and Cursor.

## Your role on pull requests

You are the first reviewer of every plugin submission. Check the pull request against the rules in the path-specific files under `.github/instructions/`:

| File | Covers |
| --- | --- |
| `plugin-submission.instructions.md` | Every plugin PR: reuse, layout, ownership, versioning, README, secrets |
| `plugin-manifest.instructions.md` | `plugin.json`, `.mcp.json`, marketplace registration |
| `plugin-skills.instructions.md` | Skill quality and structure |
| `plugin-agents.instructions.md` | Agents, commands, generated files |
| `plugin-evals.instructions.md` | Eval coverage and quality |
| `agentz-authoring.instructions.md` | Authoring conventions (also used by HVE Core `hve-builder`) |
| `agentz-evals.instructions.md` | Eval conventions (also used by HVE Core `vally-tests`) |
| `gate-changes.instructions.md` | Changes to CI, scripts, CODEOWNERS or these instructions |

## How to review

- Check every rule that applies to the changed files, including rules CI also enforces. CI is authoritative and blocks the merge; you are a second line that explains problems early and in plain language.
- Leave one inline comment per problem, on the line where it occurs. Say which rule it breaks and exactly what to change.
- Keep inline comments for problems only. Don't comment inline on things that follow the rules, and don't restate the diff. Positive findings go in the review summary.
- If you can't verify a rule from the diff (for example, whether evals pass), say what the author should confirm instead of assuming.
- When in doubt about a duplicate, raise it as a question, not a verdict.

## Review summary

Finish every review with one summary comment, whether or not changes are required. Post it even when you found no problems.

Use this structure:

```markdown
## Review summary

**Verdict:** Approve / Changes requested / Needs author confirmation

### What's good
- One bullet per rule or practice the PR follows well, naming the rule and the file.

### What needs attention
- One bullet per problem, naming the rule, the file and the fix. Link to the inline comment where one exists.
- Write "None found." when there are no problems.

### To confirm
- Rules you couldn't verify from the diff (for example, evals passing, duplicate check).
- Write "Nothing outstanding." when there is nothing.
```

Rules for the summary:

- Be specific and evidence-based. Name the rule and the file, for example "Evals meet the minimums: 13 stimuli, 4 trigger, 3 no-trigger (`plugins/<name>/evals/eval.yaml`)". Don't write generic praise such as "looks good" or "great work".
- Only praise what you checked. Don't list a rule as followed if you couldn't verify it; put it under "To confirm" instead.
- Cover the areas the PR touched (submission, manifest, skills, agents, evals, gate changes) and skip the ones it didn't.
- Use "Approve" only when "What needs attention" is empty. Use "Changes requested" when any rule is broken. Use "Needs author confirmation" when the only open items are in "To confirm".
- The summary adds to the inline comments and doesn't replace them. Don't repeat a problem's full explanation; point to the inline comment.
- CI stays authoritative. The verdict is advice and never replaces the required status checks.

## Source and generated files

Sources (edit these): each plugin's root `plugin.json`, `.mcp.json`, `skills/`, `agents/`, `commands/`, `evals/`, `README.md`, and the root `.claude-plugin/marketplace.json`.

Generated (never edited by hand): each plugin's `.claude-plugin/`, `.cursor-plugin/` and `mcp.json` (the Cursor copy of `.mcp.json`); at the root `.github/plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, `catalog.json`, and the plugins table in `README.md`. The fix for any of these is always: edit the source, then run `python3 scripts/sync_manifests.py` and `python3 scripts/build_catalog.py`.
