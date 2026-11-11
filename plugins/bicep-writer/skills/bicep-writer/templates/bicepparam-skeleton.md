# Template: .bicepparam skeleton

One `.bicepparam` file per environment, named after it (for example `dev.bicepparam`, `prod.bicepparam`).

```bicep
using './main.bicep'

param workloadName = 'contoso'
param environment = 'dev'
param location = 'australiaeast'
param tags = {
  environment: 'dev'
  managedBy: 'bicep'
}
```

Rules for generated parameter files:

- `using` points at the template the values belong to.
- Only environment-specific values live here; shared defaults stay in the template.
- Never put a secret value in this file. Secure parameters are supplied at deployment time (pipeline secret or Key Vault reference), and the summary tells the user which ones.
