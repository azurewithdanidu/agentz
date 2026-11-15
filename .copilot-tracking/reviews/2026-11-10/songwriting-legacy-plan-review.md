<!-- markdownlint-disable-file -->
---
description: "Migration and rebase review, including every shared-file conflict resolution."
---

# Songwriting migration and rebase review

Date: 2026-11-10. Reviewer: GitHub Copilot, direct review.
Status: Complete for the approved local packaging migration and rebase.

## Request fulfillment

* One songwriting agent and one English-songwriting skill in the classic layout
* No namespace folder or Agent Plugins schema in the songwriting plugin
* Preserved client manifests, marketplace identity, owner and existing eval cases
* Rebased onto latest fetched origin/main, da88d18
* Reused upstream shared files instead of replacing its completed migration
* Preserved local source work, presentation, eval artifacts and recovery snapshot

## Conflict resolutions

The rebase itself succeeded. Popping the original work stash caused ten conflicts.
Each shared file was resolved to the upstream version for these reasons:

| File | Rationale |
| --- | --- |
| [Copilot context](../../../.github/copilot-instructions.md) | Keep main's classic source/generated distinction |
| [Authoring instructions](../../../.github/instructions/agentz-authoring.instructions.md) | Follow upstream root component layout and body-based permission limits |
| [Agent instructions](../../../.github/instructions/plugin-agents.instructions.md) | Retain one shared source without tools frontmatter |
| [Manifest instructions](../../../.github/instructions/plugin-manifest.instructions.md) | Keep the upstream schema-less manifest convention |
| [Claude context](../../../CLAUDE.md) | Preserve the completed repository-wide migration guidance |
| [README](../../../README.md) | Keep main's prose; regenerate only the songwriting table entry |
| [Publishing standard](../../../docs/plugin-standard.md) | Keep the upstream classic standard, not interim mixed-format rules |
| [Catalog builder](../../../scripts/build_catalog.py) | Use main's root-level agent and command discovery |
| [Manifest synchronizer](../../../scripts/sync_manifests.py) | Keep main's metadata-only generation, which preserves authored agents |
| [Repository gate](../../../scripts/validate_repo.py) | Retain upstream classic manifest, component and version rules |

Also removed the obsolete local packaging test file and workflow addition. The
songwriter agent now states its editing/execution/network limits in its body.

## Validation

* Plugin-scoped check after adaptation: zero errors, zero warnings
* `validate_repo.py --base origin/main`: zero errors, zero warnings; both generated
  check modes succeed
* Pinned strict Vally lint: seven skills and four plugin eval specs pass
* Pinned Claude marketplace validation: passed
* Staged restoration reviewed; restored files returned to unstaged state

## Limitations and follow-up

No live IDE or model-backed rerun was performed. Previous model evals retain
their incomplete disconnected-session status. No commits or pushes were made.
The original work recovery stash is bf36534ea22bd90da425486e96aa8bde728e0393.
Next steps are client smoke tests, model eval completion and approved publication.