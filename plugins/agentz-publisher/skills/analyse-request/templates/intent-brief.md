# Intent brief: <plugin-name>

- **Status:** draft | confirmed
- **Owner:** <team> (<email>, @<github-handle>)
- **Proposed component(s):** skill `<name>` [+ agent `<name>`] [+ command `<name>`]
- **Clients:** VS Code (primary) [, Copilot CLI, Claude Code, Cursor]

## Problem

<One or two sentences.>

## Should trigger on

1. "<what a user would type>"
2. "<...>"
3. "<...>"

## Should not trigger on

1. "<nearby request>" (why: <different tool, language or action>)
2. "<...>"

## Inputs and output

- **Inputs:** <files, parameters, context>
- **Output:** <report, files, PR, ...>

## Allowed actions

- [ ] Report only
- [ ] Edit files in the user's repo
- [ ] Run local checks
- [ ] Change external systems (needs an approval step)

## Failure modes to test

1. <a wrong or harmful answer the evals must catch>
2. <...>

## Open questions

- <anything not yet decided>
