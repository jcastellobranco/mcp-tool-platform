# Implementation instructions

Inherits ../AGENTS.md.

- `tool_platform/core.py` defines the baseline Principal/Tool/Gateway. Keep existing signatures compatible.
- `tool_platform/catalog.py` defines strict argument validation and safe allowlisted tools.
- `tool_platform/mcp_server.py` is the stdio MCP transport. Do not print human-readable logs to stdout.
- Every tool call must check scopes, even when tool discovery has filtered the list.
- Avoid side-effecting tools until identity, approval, audit and idempotency are implemented.
- Add deterministic tests for security decisions and argument bounds.
