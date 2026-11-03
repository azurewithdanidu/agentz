---
name: bicep-avm-review
description: Review Azure Bicep templates and parameter files against Azure Verified Modules (AVM) and organisation IaC conventions, and produce a findings report with evidence. Use when the user asks to "review my Bicep", "check this against AVM", "is this template production ready", "audit our IaC", or opens a PR that changes *.bicep or *.bicepparam files. Do not use for Terraform, ARM JSON authoring, or for deploying resources.
---

# Bicep AVM review

Reviews Bicep code for AVM alignment, security defaults and repository conventions. Produces findings only. It does not edit files or deploy anything.

## When to use

- A user asks for a review, audit or readiness check of Bicep templates or `.bicepparam` files.
- A pull request changes `*.bicep` or `*.bicepparam` files.

## When not to use

- Terraform, Pulumi or raw ARM JSON. Say the skill does not cover them.
- Requests to fix, deploy or run `what-if`. Report findings and stop.

## Inputs and prerequisites

- **Required:** the path to one or more `.bicep` files, or a folder.
- **Optional:** the organisation's IaC conventions file, if the repository has one.
- **Permissions:** read-only access to the repository. No Azure access is needed.

## Workflow

Load each file only when you reach its step.

1. **Discover.** Follow [steps/01-discover.md](steps/01-discover.md) to list templates, modules and parameter files in scope.
2. **Check AVM alignment.** Follow [steps/02-avm-alignment.md](steps/02-avm-alignment.md), using [references/avm-rules.md](references/avm-rules.md).
3. **Check security defaults.** Follow [steps/03-security-defaults.md](steps/03-security-defaults.md), using [references/security-baseline.md](references/security-baseline.md).
4. **Report.** Write the report using [templates/findings-report.md](templates/findings-report.md).

## Safety boundaries and stop conditions

- Never edit, format or delete files. Never run `az deployment` or any command that changes Azure.
- Never print secret values found in parameter files. Report the file and line only.
- If no `.bicep` files are found, stop and say so. Do not guess at file contents.

## Evidence rules

- Every finding cites a file path and line number.
- Mark each finding as **Confirmed** (seen in code) or **Assumption** (inferred, needs checking).
- Do not infer runtime behaviour from file or module names alone.

## Outputs and completion

- **Output:** one findings report in the format of [templates/findings-report.md](templates/findings-report.md).
- **Done when:** every in-scope file is listed in the report with a status, and every finding has evidence and a severity.
