# Step 2: AVM alignment

**Purpose:** check how closely the templates follow Azure Verified Modules.

**Inputs:** the table from step 1 and [../references/avm-rules.md](../references/avm-rules.md).

**Actions:**
1. For each raw `resource` declaration, check whether an AVM resource module exists for that type. If one exists, raise a finding.
2. For each AVM module reference, check that the version is pinned, not a floating tag.
3. Apply the remaining rules in the reference file.

**Output:** findings with rule ID, file, line, severity and status (Confirmed or Assumption).

**Depends on:** step 1.
