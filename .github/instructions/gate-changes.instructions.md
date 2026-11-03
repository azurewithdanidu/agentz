---
applyTo: ".github/**,scripts/**,AGENTS.md,CLAUDE.md"
---

# Changes to the gate itself

These files define how every plugin is checked, including these review instructions. Copilot reads instructions from the pull request's own branch, so a PR can change its own review. Treat every change here with extra care.

- Flag any change that removes or weakens a check: lowering the minimum eval count, raising the duplicate threshold, removing a validation, skipping a CI job, loosening a required status check, or deleting review rules.
- Flag a plugin PR that also changes `.github/` or `scripts/`. Gate changes should come in their own pull request.
- Changes to `.github/CODEOWNERS` must not remove the marketplace owner from `/.github/`, `/scripts/` or `/.claude-plugin/`.
- Workflow changes must keep `permissions: contents: read` unless a step needs more, and must not add secrets to logs.
- Changes to `scripts/` keep both `--check` modes working and come with a note on how they were tested.
- Changes to the tool mapping in `scripts/marketplace_lib.py` must map each Copilot tool set to real Claude Code tools.
