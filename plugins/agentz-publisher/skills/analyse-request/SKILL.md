---
name: analyse-request
description: Analyse what someone wants to publish to the agentz marketplace and capture it as an intent brief before anything is built. Use when someone says "I want to publish an agent", "I have an idea for a skill", "can we share this prompt with other teams", or starts the agentz publishing flow. This is phase 1 of 4 (Analyse, Research, Build, Validate). Do not use to build or edit files, or for plugins that already exist.
---

# Analyse the request

Turns an idea into a short, checkable intent brief. Every later phase works from this brief: Research checks it against the catalog, Build writes the skill from it, and Validate turns its trigger phrases and failure modes into evals.

This skill only asks questions and writes the brief. It changes nothing else.

## When to use

- Someone wants to publish a new agent, skill or command to agentz.
- Someone wants to share an existing prompt or agent they use locally.

## When not to use

- Changing an existing plugin. Edit it directly, bump its version and open a PR.
- Installing plugins. Point to `docs/consuming-plugins.md`.

## Inputs

Ask for anything missing, a few questions at a time. Don't invent answers.

- The problem it solves, in one or two sentences.
- Who uses it and in which clients (VS Code is the primary client).
- At least three things a user would actually type that should trigger it.
- At least two nearby requests that should **not** trigger it.
- Inputs it needs and the output it produces.
- What it may do: report only, edit files, run local checks, or change external systems.
- Known failure modes: what a bad answer looks like.
- Owner: team name, email and GitHub handle.

## Workflow

1. Ask for the inputs above. If the user pastes an existing prompt or agent, extract what you can from it first and only ask for the gaps.
2. Decide the component type using [references/component-types.md](references/component-types.md). Default to a skill.
3. Write the brief to `.agentz/<plugin-name>/intent-brief.md` using [templates/intent-brief.md](templates/intent-brief.md). Propose a lowercase, hyphenated plugin name.
4. Show the brief and ask the user to confirm or correct it.
5. Hand over to the `research-catalog` skill.

## Stop conditions

- The user can't name a problem or at least three trigger phrases: stop and explain that the skill can't be tested without them.
- The request is to change external systems with no approval step: record it as an open question and say the build will add an approval gate.

## Output

- `.agentz/<plugin-name>/intent-brief.md`, confirmed by the user.
- **Done when:** every section of the template is filled in or marked as an open question.
