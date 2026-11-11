# Step 3: Write the files

**Purpose:** write the `.bicep` and `.bicepparam` files from the approved plan and module table.

**Inputs:** the module table from step 2, [../references/authoring-rules.md](../references/authoring-rules.md), [../templates/main-bicep-skeleton.md](../templates/main-bicep-skeleton.md) and [../templates/bicepparam-skeleton.md](../templates/bicepparam-skeleton.md).

**Actions:**

1. Start each new template from the skeleton and fill in the modules from the table, applying every rule in the authoring rules file.
2. Declare parameters for all environment-specific values and put their values in a `.bicepparam` file per environment, started from the bicepparam skeleton.
3. For secret inputs, declare a `@secure()` parameter or a Key Vault reference. Never write the secret value itself into any file, even when the user pasted one into the chat.
4. When changing an existing file, show the user the intended change and get approval before saving it.
5. Add outputs for values downstream templates or pipelines will need (resource IDs, endpoints, principal IDs).

**Output:** saved `.bicep` and `.bicepparam` files.

**Depends on:** steps 1 and 2.

**Stop conditions:** the user rejects a change to an existing file.
