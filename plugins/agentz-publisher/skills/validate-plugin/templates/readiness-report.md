# Publish readiness: <plugin-name> <version>

## Summary

- **Verdict:** ready | not ready
- **Research verdict:** new (closest match: `<plugin>/<skill>`, score <0.00>)
- **Evals:** <passed>/<total> passed over <runs> runs (threshold <0.7>)
- **Gate:** `validate_repo.py` <passed | n errors>

## Evals

| Case | Kind | Result | Notes |
| --- | --- | --- | --- |
| `<name>` | trigger | pass | |

## Gate checks

- [ ] Manifest and `mcp.json` valid against Agent Plugins 1.0
- [ ] Version bumped (existing plugins)
- [ ] CODEOWNERS entry
- [ ] At least 10 evals, triggers for every skill
- [ ] No secrets
- [ ] Generated files in sync

## Open items

- <anything the reviewer should know>
