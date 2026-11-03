# Step 3: Security defaults

**Purpose:** catch insecure settings before they reach a deployment.

**Inputs:** the in-scope files and [../references/security-baseline.md](../references/security-baseline.md).

**Actions:**
1. Check each rule in the baseline against every resource and module parameter.
2. For parameter files, flag literal secrets without printing their values.

**Output:** findings with rule ID, file, line, severity and status.

**Depends on:** step 1.
