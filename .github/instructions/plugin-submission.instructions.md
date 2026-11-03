---
applyTo: "plugins/**,.claude-plugin/marketplace.json,catalog.json,.github/CODEOWNERS"
---

# Plugin submission checklist

Apply to every pull request that adds or changes a plugin.

## 1. Reuse before you build

- A new plugin, skill or agent must not duplicate an existing one. Compare its name and description with the existing entries visible in `catalog.json` and the marketplace.
- If an existing skill does most of the same job, comment with its name and recommend extending it instead.
- If two skills would trigger on the same prompts, name the prompts that collide.
- CI posts a "possible duplicate" warning based on description similarity. Treat it as a lead and explain whether the overlap is real.
- If you can't see enough of the catalog to judge, ask the author to confirm the reuse check in the PR description, or to attach the `research.md` verdict from the `agentz-publisher` flow.

## 2. Layout

- The plugin folder is `plugins/<name>/`, and `<name>` is lowercase letters, digits and hyphens, at most 64 characters.
- The folder name, `plugin.json` name and marketplace entry name are identical.
- Required: `plugin.json`, at least one `skills/<skill>/SKILL.md`, `evals/eval.yaml` (Vally format), `README.md`.
- Not allowed: a top-level `bin/` folder (Claude org sync rejects the plugin; use `scripts/`), `hooks.json` at the plugin root, a legacy `.plugin/` folder.

## 3. Ownership

- `.github/CODEOWNERS` has a line `/plugins/<name>/ <owner>` for every new plugin.
- The `author` in `plugin.json` names the owning team and an email.

## 4. Versioning

- Any change to a plugin's sources needs a version bump in its root `plugin.json`: patch for fixes, minor for new behaviour, major for breaking changes.
- `0.x` is beta and `1.0.0` or later is stable. Promotion is a version bump, never a rename.
- A rename or removal needs an entry in the `renames` map of `.claude-plugin/marketplace.json`.

## 5. README

- States owner, status (beta or stable), format, platforms, install line and a usage example.
- The usage example matches what the skills actually do.

## 6. Secrets and safety

- Flag anything that looks like a key, token, password, connection string or private key, in any file.
- Flag internal URLs, organisation names or policies copied from another organisation.
