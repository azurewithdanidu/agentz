<!-- markdownlint-disable-file -->
---
description: "Execution details for the songwriting legacy migration."
---

# Migration details

1. Stash tracked/untracked local work and separately preserve Vally outputs that
   become untracked when the local ignore rule is stashed. Rebase onto origin/main.
2. Resolve overlapping shared files to upstream's classic-layout implementation.
   Remove interim mixed-format tests and the local CI addition, which are obsolete.
3. Keep songwriting's shared root agent, schema-less manifest and version 0.2.0.
   Remove the agent's tools field under upstream rules and state its limits in the
   body. Do not alter the songwriting skill or Vally cases.
4. Restore the presentation and Vally artifacts, retain the original recovery
   stash, regenerate the README table and return restored edits to unstaged state.
5. Run repository validation against origin/main, full strict Vally lint and pinned
   Claude validation. Review staged restoration, diff hygiene and branch ancestry.
   Disclose that live-client and model-backed behavior were not retested.

See the related plan and research documents under `.copilot-tracking/`.