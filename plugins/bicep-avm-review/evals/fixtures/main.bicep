// Fixture for evals: minimal template that references a parameter file.
param adminPassword string
param location string = resourceGroup().location

output region string = location
