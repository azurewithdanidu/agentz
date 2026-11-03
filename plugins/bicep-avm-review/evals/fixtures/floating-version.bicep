// Fixture for evals: module version is not pinned to an exact version.
param location string = resourceGroup().location

module storage 'br/public:avm/res/storage/storage-account:0' = {
  name: 'storage'
  params: {
    name: 'stevalsfixture001'
    location: location
  }
}
