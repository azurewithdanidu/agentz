# Finding and referencing AVM modules

How to map an Azure resource to an Azure Verified Modules (AVM) module and reference it from Bicep.

## Module reference syntax

```bicep
module storageAccount 'br/public:avm/res/storage/storage-account:0.14.3' = {
  name: 'storage-account-deployment'
  params: {
    name: storageAccountName
  }
}
```

The path is `br/public:avm/<class>/<service>/<resource>:<version>`:

- `res`: resource modules, one per Azure resource type. Default choice.
- `ptn`: pattern modules composing several resources (for example a landing zone). Use only when the user asks for that pattern.
- `utl`: utility modules (helpers with no resources of their own).

## Where to look modules up

Check in this order and record which source confirmed the module:

1. **The AVM index** at <https://aka.ms/avm> (Bicep resource modules page). It lists every published module with its registry path and status.
2. **A Bicep-aware tool**, when the client provides one (for example an MCP tool that lists AVM metadata or resource schemas). Use it to confirm available versions and parameter names.
3. **The module source** at <https://github.com/Azure/bicep-registry-modules> under `avm/res/<service>/<resource>`, where `README.md` documents every parameter, required and optional.

If none of these confirm a module for the resource type, treat it as not existing and fall back to a raw `resource` declaration, marked as an assumption.

## Version pinning

- Always pin an exact `MAJOR.MINOR.PATCH` version taken from the index or the registry tags. Never use `latest` or omit the version.
- Most AVM modules are `0.x`: minor versions may break. Record the pinned version in the summary so reviewers can check it.

## Parameter mapping

- Required parameters (usually only `name`) must come from template parameters, not literals.
- `location` defaults to `resourceGroup().location` in most modules; set it explicitly only when the user asked for a specific region.
- Prefer the module's built-in interfaces (`tags`, `diagnosticSettings`, `roleAssignments`, `privateEndpoints`, `managedIdentities`) over separate resources.
