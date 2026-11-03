---
applyTo: "plugins/*/plugin.json,plugins/*/mcp.json,.claude-plugin/marketplace.json"
---

# Manifest and MCP rules

## Plugin manifest: `plugins/<name>/plugin.json`

- `$schema` is exactly `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`.
- Allowed top-level fields only: `$schema`, `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `extensions`. Flag anything else (for example `displayName`, `category`, `agents`, `hooks`): the Agent Plugins schema is closed.
- `name` matches the folder name.
- `version` is semantic versioning (`MAJOR.MINOR.PATCH`) and higher than before if the plugin changed.
- `description` is present and says what the plugin does in one or two sentences.
- `author` is an object with `name` and `email`, and optionally `url`. Nothing else.
- `extensions`, if present, is an object keyed by namespace, such as `{"com.github.copilot": {}}`.

## MCP servers: `plugins/<name>/mcp.json`

- `$schema` is exactly `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json`.
- Only `$schema` and `mcpServers` at the top level.
- Each server has a `type` of `stdio` or `streamable-http`. `sse` is deprecated. Claude's `http` is wrong here; it belongs only in the generated `.mcp.json`.
- `stdio` servers need `command`, a single executable name or a `./` path inside the plugin. `streamable-http` servers need `url`.
- No credentials in `env`, `headers` or `url`. Authentication belongs to the client.
- Flag servers that aren't needed by the plugin's skills.

## Marketplace registration: `.claude-plugin/marketplace.json`

- Every plugin folder has exactly one entry, and every entry has a folder.
- `source` is `./plugins/<name>` (relative, starting with `./`).
- `category` is one of `productivity`, `development`, `security`, `observability`.
- `description` is present.
- `version` is not set on the entry; it lives in the plugin's `plugin.json`.
