# Step 1: Discover

**Purpose:** build the list of files in scope before reviewing anything.

**Inputs:** the path the user gave.

**Actions:**
1. List every `*.bicep` and `*.bicepparam` file under the path.
2. For each template, record the `targetScope` and every `module` reference.
3. Classify each module reference as **AVM registry** (`br/public:avm/...`), **private registry** (`br:<registry>/...`) or **local** (relative path).

**Output:** a table of files with scope and module references.

**Stop if:** no Bicep files are found. Report that and end the review.
