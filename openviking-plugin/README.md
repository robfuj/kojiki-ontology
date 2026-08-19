# Kojiki Viking Memory — OpenViking Agent Plugin (Agent Plugins 1.0)

An [Agent Plugins 1.0](https://agent-plugins.org/specification) package that gives any Kojiki
Decision System agent durable, observable long-term memory via [OpenViking](https://github.com/volcengine/OpenViking).

A plugin is a plain directory with a `plugin.json` manifest, an `mcp.json` declaring the
`openviking` MCP server, and a `skills/kojiki-viking-memory/SKILL.md` that teaches the model the
recall + persist loop. Any Agent-Plugins-conforming client (Cursor, VS Code, OpenAI/Amazon-side
clients, and Hermes when wired) loads it the same way.

## Contents
```
plugin.json                              # Agent Plugins 1.0 manifest
mcp.json                                 # stdio MCP server: "openviking"
skills/kojiki-viking-memory/SKILL.md     # teaches recall + persist of Decision Objects + Ledger
servers/                                 # OpenViking stdio->HTTP proxy (fetch from OpenViking, see SKILL.md)
```

## Install
1. Have an OpenViking server reachable (default local `http://127.0.0.1:1933`).
2. Fetch the proxy (OpenViking is external AGPL — not vendored):
   ```bash
   mkdir -p servers
   curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/agent-plugins/servers/mcp-proxy.mjs -o servers/mcp-proxy.mjs
   curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/agent-plugins/servers/config.mjs   -o servers/config.mjs
   curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/agent-plugins/servers/debug-log.mjs -o servers/debug-log.mjs
   ```
3. Point your Agent-Plugins-conforming client at this directory. The client registers the
   `openviking` MCP server and discovers the `kojiki-viking-memory` skill.
4. Set credentials if not local: `OPENVIKING_URL` / `OPENVIKING_API_KEY` (or `~/.openviking/ov.conf`).

## What the agent gains
- `find` / `search` / `read` — recall prior decisions and learning (context mode assembles surrounding context).
- `remember` / `write` — persist Decision Objects + Learning Ledger entries to `viking://`, so
  organizational learning survives across sessions and is browsable, not a black box.

This makes the Kojiki principle "exceptions are learning" durable: every outcome the agent
records becomes queryable memory for its siblings.
