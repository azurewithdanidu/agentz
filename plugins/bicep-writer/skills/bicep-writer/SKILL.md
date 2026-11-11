---
name: bicep-writer
description: Write new Azure Bicep templates and .bicepparam files composed from Azure Verified Modules (AVM), with pinned module versions, secure defaults and a local compile check. Use when the user asks to "write Bicep for", "create a Bicep template", "generate Azure IaC in Bicep", or "add an AVM module to this template". Do not use for reviewing or auditing existing Bicep, for Terraform, Pulumi or raw ARM JSON authoring, or for deploying resources to Azure.
---

# Bicep writer

Writes new Bicep templates and parameter files by composing Azure Verified Modules (AVM). It creates and edits `.bicep` and `.bicepparam` files and runs a local compile check. It never deploys anything.

## When to use

- A user asks for new Bicep code for one or more Azure resources.
- A user asks to add a resource or module to an existing Bicep template.

## When not to use

- Reviewing, auditing or assessing existing Bicep. Point the user at a review skill instead.
- Terraform, Pulumi or raw ARM JSON. Say the skill does not cover them.
- Deploying, running `what-if`, or any command that changes Azure. Write the files and stop.

## Inputs and prerequisites

- **Required:** which Azure resources to create, and where the files should go (a target folder or file path).
- **Optional:** environment names, region, naming convention, tags, and an existing template to extend.
- **Permissions:** read and write access to the repository. No Azure access is needed. The Bicep CLI (or `az bicep`) is optional and only used for the local compile check.

## Workflow

Load each file only when you reach its step.

1. **Gather requirements.** Follow [steps/01-gather-requirements.md](steps/01-gather-requirements.md) to confirm resources, target paths and conventions, and present a short plan. **Wait for the user to approve the plan before writing any file.**
2. **Select modules.** Follow [steps/02-select-modules.md](steps/02-select-modules.md), using [references/module-selection.md](references/module-selection.md) to map each resource to a pinned AVM module.
3. **Write the files.** Follow [steps/03-write-template.md](steps/03-write-template.md), applying [references/authoring-rules.md](references/authoring-rules.md) and starting from [templates/main-bicep-skeleton.md](templates/main-bicep-skeleton.md) and [templates/bicepparam-skeleton.md](templates/bicepparam-skeleton.md).
4. **Verify.** Follow [steps/04-verify.md](steps/04-verify.md) to compile the files locally and report what was written.

## Safety boundaries and stop conditions

- Never run `az deployment`, `az stack`, or any command that creates, changes or deletes Azure resources. If the user asks to deploy, write the files, then say deployment is outside this skill.
- Never write a secret value into a `.bicep` or `.bicepparam` file, even when the user supplies one. Use a `@secure()` parameter or a Key Vault reference and tell the user where to supply the value.
- Never overwrite an existing file without first showing the user what will change and getting approval.
- If the user cannot say which resources they need, stop and ask. Do not invent an architecture.

## Evidence rules

- Cite the AVM module index as the source for each module name, and mark the version used.
- Mark module parameter usage as **Confirmed** (checked against the module's documentation or schema) or **Assumption** (inferred, needs checking before deployment).

## Outputs and completion

- **Output:** one or more `.bicep` files, matching `.bicepparam` files where environment values are needed, and a short summary listing each file, the modules used with their pinned versions, and any assumptions.
- **Done when:** every requested resource is represented by a module or a documented raw-resource fallback, the files compile (or the compile check was unavailable and this is stated), and the summary is delivered.
