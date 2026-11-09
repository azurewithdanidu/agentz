# Choosing the component type

Skills and MCP servers work in every client. Agents work in Copilot and Claude Code. Pick the most portable type that does the job.

| Need | Use | Where it lives |
| --- | --- | --- |
| Reusable knowledge or a workflow the model should apply when relevant | **Skill** (default) | `skills/<name>/SKILL.md` |
| A persona with a fixed tool set that hands work to skills | **Agent** (keep thin) | `agents/<name>.agent.md` (no `tools` list) |
| An action the user starts explicitly with a slash command | **Command** | `commands/<name>.md` |
| Access to an external system or API | **MCP server** | `.mcp.json` |
| Code that must run on an event | **Hook** (avoid in shared plugins; formats differ between clients) | Not supported in shared plugins |

Rules of thumb:

- If you'd describe it with "when the user asks…", it's a skill.
- If it needs its own persona or a separate context, add a thin agent that calls the skill.
- Logic in an agent only works in clients that load that agent. Logic in a skill works everywhere.
