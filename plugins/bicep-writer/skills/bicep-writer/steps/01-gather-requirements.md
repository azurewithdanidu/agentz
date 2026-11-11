# Step 1: Gather requirements

**Purpose:** pin down what to build and where, before any file is written.

**Inputs:** the user's request, and the repository's existing IaC layout if one exists.

**Actions:**

1. List the Azure resources the user asked for. If the request names no concrete resource (for example "write me some Bicep"), stop and ask which resources and services they need.
2. Confirm the target path for new files. Prefer the repository's existing IaC folder (commonly `infra/` or `bicep/`); otherwise propose one.
3. Note environment-specific inputs: environments (dev, prod), region, naming convention, required tags. Where the user gives none, plan parameters with sensible placeholder values and flag them as assumptions.
4. Check whether any target file already exists. If it does, the plan must say the file will be extended or changed, not silently replaced.
5. Present a short plan: resources, files to create or change, and parameters. **Ask the user to approve it.**

**Output:** an approved plan listing resources, target files and parameters.

**Stop conditions:** no concrete resources named, or the user does not approve the plan.
