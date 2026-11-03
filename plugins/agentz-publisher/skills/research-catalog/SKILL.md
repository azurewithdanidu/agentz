---
name: research-catalog
description: Search the agentz marketplace catalog for plugins, skills, agents and commands that already do what a new one would, and return a reuse, extend or new verdict. Use when someone asks "does agentz already have", "is there a skill for", or plans a new agent, skill or plugin. Use during research, including with rpi-research, and before hve-builder creates an artifact for agentz. This is phase 2 of 4 (Analyse, Research, Build, Validate). Do not use to build anything or to review an open pull request.
---

# Research the catalog

Answers one question before anything is built: does agentz already have this? It returns one of three verdicts:

- **Reuse:** an existing plugin already does the job. Install it.
- **Extend:** an existing plugin does most of the job. Contribute to it through its owner.
- **New:** nothing close exists. Build a new plugin.

This skill reads only. It writes one research file and changes nothing else.

## When to use

- Phase 2 of the agentz publishing flow, after `analyse-request`.
- During HVE `rpi-research`, or before `hve-builder` creates an agent or skill in this repository.

## When not to use

- Reviewing a pull request. CI and Copilot review already compare PRs with the catalog.

## Inputs

- `.agentz/<plugin-name>/intent-brief.md` from the Analyse phase. If it doesn't exist, ask for the problem and trigger phrases, or run `analyse-request` first.
- `catalog.json` at the repository root. If you're not in the agentz repository, ask the user to clone `azurewithdanidu/agentz` first.

## Workflow

1. Run the search with the brief's problem statement and trigger phrases:

   ```bash
   python3 plugins/agentz-publisher/skills/research-catalog/scripts/search_catalog.py \
     --catalog catalog.json --query "<problem statement and trigger phrases>"
   ```

   It ranks every skill, agent and command by overlap, using the same scoring as the CI duplicate check.
2. Read the description of every match scoring 0.4 or higher. Scores are leads, not verdicts: decide by comparing what each match actually does with the brief.
3. Apply the decision rules in [references/verdict-rules.md](references/verdict-rules.md).
4. Write `.agentz/<plugin-name>/research.md` using [templates/research.md](templates/research.md). Cite each match by plugin and skill name, with its score.
5. Report the verdict:
   - **Reuse:** give the install command and stop.
   - **Extend:** name the plugin, its owner from `.github/CODEOWNERS`, and what to add. Stop; the change goes to that plugin.
   - **New:** state why the closest match isn't enough, then hand over to `build-plugin`.

## Stop conditions

- `catalog.json` is missing: stop and ask the user to run the command from the agentz repository root.
- The verdict is reuse or extend: don't continue to Build unless the user gives a reason, and record that reason in the research file.

## Output

- `.agentz/<plugin-name>/research.md` with the matches, scores, verdict and reasoning.
- **Done when:** the verdict is recorded and, for **new**, the closest match is named with the reason it isn't enough.
