# Choosing the component type

Agent Plugins 1.0 makes only skills and MCP servers portable across clients. Pick the most portable type that does the job.

| Need | Use | Where it lives |
| --- | --- | --- |
| Reusable knowledge or a workflow the model should apply when relevant | **Skill** (default) | `skills/<name>/SKILL.md` |
| A persona with a fixed tool set that hands work to skills | **Agent** (keep thin) | `com.github.copilot/agents/<name>.agent.md` |
| An action the user starts explicitly with a slash command | **Command** | `com.github.copilot/commands/<name>.md` |
| Access to an external system or API | **MCP server** | `mcp.json` |
| Code that must run on an event | **Hook** (avoid in shared plugins) | `com.github.copilot/hooks/hooks.json` |

Rules of thumb:

- If you'd describe it with "when the user asks…", it's a skill.
- If it needs its own tool restrictions or a separate context, add a thin agent that calls the skill.
- Logic in an agent only works in clients that load that agent. Logic in a skill works everywhere.
