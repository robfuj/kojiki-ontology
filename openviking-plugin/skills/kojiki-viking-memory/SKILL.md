---
name: kojiki-viking-memory
description: Use when a Kojiki Decision System agent needs to recall or persist organizational learning (Decision Objects, Learning Ledger entries, rules) in long-term memory via an OpenViking server. Trigger at task start (recall prior decisions) and after every decision (persist the outcome + learning).
---

# Kojiki Viking Memory

Give a Kojiki department agent durable, observable long-term memory backed by
[OpenViking](https://github.com/volcengine/OpenViking) — an open-source context database that
stores memories, resources, and skills under a `viking://` virtual filesystem with tiered
(L0 abstract / L1 overview / L2 details) on-demand loading and a watchable retrieval trajectory.

This skill assumes the `openviking` MCP server (declared in this plugin's `mcp.json`) is
reachable. It exposes tools such as `find`, `search`, `read`, `remember`, `write`.

## When to recall (task start)
Before acting on a decision, check whether the org already decided something similar:
- `search` with `mode="context"` for server-assembled relevant context, or
- `find "what did we decide about <topic>"` then `read` the highest-scoring entry.

Persist findings as a Decision Object reference so the agent doesn't re-litigate settled calls.

## When to persist (after every decision)
After a decision resolves, write the Learning Ledger entry (docx S7) and the Decision Object
(docx S9) to `viking://` under the owning department:
- `remember` / `write` the case: Decision → Assumption → Action → Expected → Actual → Variance →
  Cause → Learning → Rule.
- Tag with the department (e.g. `kojiki-security-department`) and the `decision_id` so it is
  discoverable by sibling agents via `find`.

## Mapping to the Kojiki schemas
| Kojiki record | viking:// location |
|---|---|
| Decision Object (S9) | `viking://resources/<dept>/decisions/<decision_id>` |
| Learning Ledger (S7) | `viking://resources/<dept>/learning/<decision_id>` |
| Rule (versioned) | `viking://resources/<dept>/rules/<rule_id>` |
| Exception | `viking://resources/<dept>/learning/exceptions/<decision_id>` |

## Config
The OpenViking MCP proxy resolves its server URL + key at runtime from the same sources as the
`ov` CLI: env `OPENVIKING_URL` / `OPENVIKING_API_KEY`, or `~/.openviking/ov.conf`. Default local
endpoint `http://127.0.0.1:1933` (no auth in local mode).

## Install note
The `mcp.json` here points at `servers/mcp-proxy.mjs`. That proxy is OpenViking's stdio→HTTP
bridge (Agent Plugins 1.0 format); fetch it from the OpenViking repo rather than vendoring:
```bash
mkdir -p servers
curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/agent-plugins/servers/mcp-proxy.mjs -o servers/mcp-proxy.mjs
curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/agent-plugins/servers/config.mjs -o servers/config.mjs
curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/agent-plugins/servers/debug-log.mjs -o servers/debug-log.mjs
```
OpenViking itself is an external AGPL-3.0 project and is NOT bundled in this repo.
