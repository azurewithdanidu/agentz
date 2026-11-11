---
applyTo: "plugins/*/plugin.json,plugins/*/.mcp.json,.claude-plugin/marketplace.json"
---

# Manifest and MCP rules

## Plugin manifest: `plugins/<name>/plugin.json`

- No `$schema` and no `extensions`. Those belong to the Agent Plugins 1.0 format, which agentz does not use for plugins.
- Allowed top-level fields only: `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`. Flag anything else (for example `displayName`, `category`, `agents`, `hooks`).
- `name` matches the folder name.
- `version` is semantic versioning (`MAJOR.MINOR.PATCH`) and higher than before if the plugin changed.
- `description` is present and says what the plugin does in one or two sentences.
- `author` is an object with `name` and `email`, and optionally `url`. Nothing else.

## MCP servers: `plugins/<name>/.mcp.json`

- Only `mcpServers` at the top level.
- Each server has a `type` of `stdio` or `http`. `sse` is deprecated.
- `stdio` servers need `command`, a single executable name or a `./` path inside the plugin. `http` servers need `url`.
- No credentials in `env`, `headers` or `url`. Authentication belongs to the client.
- Flag servers that aren't needed by the plugin's skills.
- `mcp.json` (no dot) in a plugin is the generated Cursor copy. Never edit it.

## Marketplace registration: `.claude-plugin/marketplace.json`

- Every plugin folder has exactly one entry, and every entry has a folder.
- `source` is `./plugins/<name>` (relative, starting with `./`).
- `category` is one of `productivity`, `development`, `security`, `observability`.
- `description` is present.
- `version` is not set on the entry; it lives in the plugin's `plugin.json`.
