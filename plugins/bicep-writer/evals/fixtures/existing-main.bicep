targetScope = 'resourceGroup'

@description('Workload name used in resource names.')
param workloadName string

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Tags applied to every resource.')
param tags object = {}

module storageAccount 'br/public:avm/res/storage/storage-account:0.14.3' = {
  name: 'storage-${workloadName}'
  params: {
    name: 'st${workloadName}demo'
    location: location
    tags: tags
  }
}

output storageAccountResourceId string = storageAccount.outputs.resourceId
