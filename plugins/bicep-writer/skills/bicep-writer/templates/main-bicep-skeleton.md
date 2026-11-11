# Template: main Bicep file skeleton

Start new templates from this shape. Replace the storage module with the modules from the step 2 table, one `module` block per resource.

```bicep
targetScope = 'resourceGroup'

@description('Workload name used in resource names.')
@minLength(3)
@maxLength(12)
param workloadName string

@description('Deployment environment.')
@allowed(['dev', 'test', 'prod'])
param environment string

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Tags applied to every resource.')
param tags object = {}

module storageAccount 'br/public:avm/res/storage/storage-account:0.14.3' = {
  name: 'storage-${workloadName}-${environment}'
  params: {
    name: 'st${workloadName}${environment}'
    location: location
    tags: tags
  }
}

@description('Resource ID of the storage account.')
output storageAccountResourceId string = storageAccount.outputs.resourceId
```

Conventions shown here that every generated file keeps:

- `targetScope` declared on the first line.
- Every parameter has `@description()`, and constraints where the service enforces them.
- Modules referenced with exact pinned versions.
- `tags` passed through from a single parameter.
- Outputs expose what downstream templates need.
