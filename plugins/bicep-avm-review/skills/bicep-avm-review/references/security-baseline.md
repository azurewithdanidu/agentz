# Security baseline

| ID | Rule | Severity |
| --- | --- | --- |
| SEC-01 | Public network access is disabled unless a decision record allows it. | High |
| SEC-02 | Storage accounts require TLS 1.2 or later and disallow shared key access where supported. | High |
| SEC-03 | Key Vaults use RBAC authorisation with soft delete and purge protection on. | High |
| SEC-04 | No secrets as literal values in templates or parameter files. Use Key Vault references or `@secure()` parameters. | Critical |
| SEC-05 | Managed identity is used instead of keys or connection strings where the service supports it. | Medium |

> **To confirm with the destination organisation:** exceptions process and the decision record location.
