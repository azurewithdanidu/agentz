# Bicep authoring rules

This is the single source for the writing rules. Steps link here and do not repeat the rules.

| ID | Rule | Severity |
| --- | --- | --- |
| WRT-01 | Compose from AVM resource modules when one exists for the type; write a raw `resource` only as a documented fallback. | High |
| WRT-02 | Pin every module reference to an exact version, never a floating tag such as `latest`. | High |
| WRT-03 | Never write a secret value into a `.bicep` or `.bicepparam` file; declare a `@secure()` parameter or a Key Vault reference instead. | High |
| WRT-04 | Keep the module's secure defaults; do not enable public network access, lower the minimum TLS version, or disable HTTPS-only unless the user explicitly asks and the summary records it. | High |
| WRT-05 | Parameterise environment-specific values (names, location, SKUs, address spaces); put the values in a `.bicepparam` file per environment. | Medium |
| WRT-06 | Pass `tags` to every module that accepts them, sourced from a single `tags` parameter or variable. | Low |
| WRT-07 | Declare `targetScope` explicitly and add outputs for values downstream templates or pipelines need. | Low |
| WRT-08 | Give every parameter a `@description()` decorator, and constrain values with `@allowed`, `@minLength` or `@maxLength` where the service enforces limits. | Low |

> **To confirm with the destination organisation:** whether a private registry mirror of AVM is required, the approved module version policy, and the mandatory tag set.

**Authoritative source:** the AVM module index at <https://aka.ms/avm>.
