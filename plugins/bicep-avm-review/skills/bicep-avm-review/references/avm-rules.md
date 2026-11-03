# AVM alignment rules

This is the single source for AVM rules. Steps link here and do not repeat the rules.

| ID | Rule | Severity |
| --- | --- | --- |
| AVM-01 | Use an AVM resource module instead of a raw `resource` when one exists for the type. | Medium |
| AVM-02 | Pin AVM module versions to an exact version. | High |
| AVM-03 | Pass `tags` to every module that accepts them. | Low |
| AVM-04 | Enable diagnostic settings through the module's `diagnosticSettings` parameter where supported. | Medium |
| AVM-05 | Use the module's `roleAssignments` parameter rather than separate role assignment resources. | Low |

> **To confirm with the destination organisation:** whether a private registry mirror of AVM is required, and the approved version policy.

**Authoritative source:** the AVM module index at https://aka.ms/avm.
