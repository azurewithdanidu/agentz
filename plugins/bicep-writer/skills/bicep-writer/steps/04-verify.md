# Step 4: Verify and report

**Purpose:** confirm the written files compile, and summarise the result.

**Inputs:** the files written in step 3.

**Actions:**

1. If the Bicep CLI is available, run `bicep build <file>` (or `az bicep build --file <file>`) on each written `.bicep` file. These commands only compile locally; they touch nothing in Azure.
2. Fix compile errors in the written files and re-run the check until it passes.
3. If no Bicep CLI is available, skip the check and state in the summary that the files were not compiled.
4. Write the summary: each file created or changed, each module with its pinned version, parameters the user must supply (especially secure ones), and every assumption from steps 2 and 3.
5. Do not deploy. If the user asked for deployment, say that deployment is outside this skill and hand the files over.

**Output:** a compile result per file and the final summary.

**Depends on:** step 3.

**Stop conditions:** a compile error that originates outside the written files (for example a broken pre-existing module); report it instead of editing unrelated files.
