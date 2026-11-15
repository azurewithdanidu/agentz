<!-- markdownlint-disable-file -->
---
description: "Final local changes after adopting main's classic plugin layout."
---

# Songwriting classic-layout changes

Date: 2026-11-10. Plan: songwriting-legacy-plan.instructions.md under the plans directory.

## Final changes relative to main

* Added songwriting 0.2.0 with one shared agent, one English-songwriting skill,
  supporting craft guidance, templates, 16 Vally cases and a lyric fixture.
* Added marketplace registration and CODEOWNERS ownership, with generated client
  manifests, catalog and README table entries.
* Added `/vally-results/` to the root ignore rules.
* Updated local publishing/tracking notes to reflect current validation and rebase.

## Superseded local work

Main already implements the classic layout. Removed the interim mixed-format
scripts, tests, workflow step and instruction edits from the final local diff.
Main's scripts, shared instructions and plugin standard are retained unchanged.
The old namespace agent and generated duplicate are absent from songwriting.

## Rebase and recovery

Rebased feature/sample-skill-for-testing onto origin/main at da88d18. There were
no branch-only commits to replay. Resolved ten stash-restoration conflicts to
upstream versions, retaining plugin registration and regenerating the README.
Restored the original presentation and local eval outputs. Recovery stash:
bf36534ea22bd90da425486e96aa8bde728e0393. No commits or pushes were created.

## Release status

Structural gates pass. Live IDE loading and full model evals remain unverified;
earlier model trials had session disconnects. Remote publication needs approval.