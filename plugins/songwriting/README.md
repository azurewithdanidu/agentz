---
description: "Original English songwriting skill and songwriter agent for agentz."
---

# Songwriting

Draft original English songs, finish a chorus, or revise lyrics for natural rhyme,
clear storytelling and singable phrasing.

* Owner: Azure with Danidu (@azurewithdanidu, danidu@dckloud.com)
* Status: beta (`0.2.0`)
* Format: legacy Copilot plugin, with generated Claude Code and Cursor manifests
* Platforms: VS Code (primary), Copilot CLI, Claude Code and Cursor; agent availability depends on the client
* Skill: [english-songwriting](skills/english-songwriting/SKILL.md)
* Agent: [songwriter](agents/songwriter.agent.md)

The root manifest has no Agent Plugins schema. The shared agent is authored
directly in `agents/`, alongside the shared `skills/` directory. Its body and skill
state the permission limits instead of using client-specific tool lists. No client
namespace folder or separate generated agent copy is needed.

## Install

With the agentz marketplace already registered in Copilot CLI:

```bash
copilot plugin install songwriting@agentz
```

See the [marketplace installation guide](../../docs/consuming-plugins.md) for other clients.
The plugin must be published to the marketplace's tracked branch before remote installation.

## Usage

Select the `songwriter` agent where supported, or ask for English songwriting:

```text
Write an original English pop song about starting over after moving cities.
Use a hopeful first-person voice, two verses, a chorus and a bridge.
```

```text
Help me finish this English chorus. Keep my first two lines unchanged
and suggest two different endings with natural rhymes.
```

```text
Improve the rhyme and singability of lyrics/my-song.md.
Show the revision in chat first; do not edit the file yet.
```

The skill drafts in chat by default. It creates or edits lyric files only when
requested, preserves material outside the revision scope, and does not generate
audio, run commands, install software or publish songs.

## Validation

[Vally evals](evals/eval.yaml) cover triggering, non-triggering, structure,
revision constraints, file permissions, originality and unsupported requests.

```bash
npx -y @microsoft/vally-cli@0.20.0 lint plugins/songwriting/skills --eval-spec plugins/songwriting/evals/eval.yaml --strict
npx -y @microsoft/vally-cli@0.20.0 eval --eval-spec plugins/songwriting/evals/eval.yaml --require-pass
```

Model-backed evals require a Copilot sign-in and may consume model usage.