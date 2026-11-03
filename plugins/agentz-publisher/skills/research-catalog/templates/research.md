# Research: <plugin-name>

- **Brief:** `.agentz/<plugin-name>/intent-brief.md`
- **Catalog:** `catalog.json` (<number> plugins)
- **Verdict:** reuse | extend | new

## Closest matches

| Plugin | Component | Score | Same job? | Notes |
| --- | --- | --- | --- | --- |
| `<plugin>` | skill `<name>` | 0.00 | yes / partly / no | <what it does and doesn't cover> |

## Reasoning

<Why this verdict. For "new", why the closest match isn't enough. For "extend", what to add and where.>

## Next step

- Reuse: `/plugin install <plugin>@agentz` (or the VS Code / Copilot CLI equivalent)
- Extend: contact <owner>; change `plugins/<plugin>/...`
- New: continue with `build-plugin`
