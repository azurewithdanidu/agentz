---
name: essay-writer
description: Plan, draft and review essays to a shared house style. Use when the user asks to "write an essay", "outline an essay", "help me structure my argument", "improve my draft", or "review this essay". Produces an outline for approval first, then a draft, or a findings report for an existing draft. Do not use for code, emails, cover letters, marketing copy, meeting summaries or fiction.
---

# Essay writer

Helps a person plan, draft or review an essay. It follows the house style in [references/house-style.md](references/house-style.md). Outline first, draft second, and it never invents sources.

## When to use

- The user wants an essay written, outlined or restructured.
- The user shares an essay draft and wants feedback or a review.

## When not to use

- Code, emails, cover letters, marketing copy, meeting notes or fiction. Say the skill does not cover them.
- Requests to cite or verify academic sources. The skill cannot look sources up. See the sourcing rule below.

## Inputs and prerequisites

- **Required for a new essay:** the topic. If it is missing, stop and ask for it.
- **Optional:** audience, target length, the position to argue, any notes or a draft file.
- **Permissions:** read-only. The skill writes a file only when the user gives a path to save to.

## Workflow

Load each file only when you reach its step.

1. **Clarify the brief.** Confirm topic, audience, length and position. Ask for anything missing, one short question at a time. If the topic is missing, stop here.
2. **Outline.** Write the outline using [templates/outline.md](templates/outline.md). Stop and ask the user to approve or change the outline. Do not draft until they do.
3. **Draft.** After approval, write the essay to the length asked, following [references/house-style.md](references/house-style.md).
4. **Check.** Before showing the draft, check it against every rule in the house style. Fix what fails.
5. **Review mode.** If the user shares an existing draft, skip steps 2 and 3. Read it and report findings using [templates/feedback-report.md](templates/feedback-report.md). Give each finding its rule ID and a quote from the draft. Do not edit the draft unless the user asks.

## Safety boundaries and stop conditions

- Never invent a source, quote, statistic, author or DOI. Where a claim needs evidence you cannot supply, write `[citation needed]` and say so.
- Never print secrets, keys or tokens found in notes or files the user shares. Mention that they are present and leave them out.
- Never edit or overwrite the user's files unless they ask for it and give the path.
- If the user says the essay is for an assessment that bans AI help, offer an outline or feedback only.

## Output and completion

- New essay: an approved outline, then the draft, then a short list of the rule checks that passed.
- Review: a findings report only.
- Done when the user has what they asked for and every claim is either supported or marked `[citation needed]`.
