# Step 2: Select AVM modules

**Purpose:** map every resource in the approved plan to a pinned AVM module.

**Inputs:** the plan from step 1 and [../references/module-selection.md](../references/module-selection.md).

**Actions:**

1. For each resource, look up the matching AVM resource module using the sources in the reference file.
2. Record the full module reference with an exact pinned version, for example `br/public:avm/res/storage/storage-account:0.14.3`.
3. Identify the module parameters the plan needs (name, location, SKU, tags, networking) and where each value will come from: a template parameter, a `.bicepparam` value, or a module default.
4. If no AVM module exists for a resource type, plan a raw `resource` declaration, mark it as an **Assumption** that no module exists, and say so in the final summary.

**Output:** a module table: resource, module reference with pinned version, parameters to set, and the source checked.

**Depends on:** step 1.

**Stop conditions:** none. Unresolvable lookups become raw-resource fallbacks with an assumption note.
