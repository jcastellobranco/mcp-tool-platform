# MCP Tool Platform

A standalone **local-first Model Context Protocol (MCP) tool server** with explicit scope checks, bounded inputs and deterministic tests.

> **Status:** Educational portfolio/reference implementation. The MCP stdio transport is implemented; this is **not** a public authenticated, multi-tenant gateway.

## Features

- MCP Python SDK `FastMCP` server using **stdio**
- Scope-gated tool discovery and execution (deny by default)
- `word_count` tool: `text:read` permission
- `sha256_text` tool: `text:hash` permission
- Bounded text inputs (max 10,000 characters), deterministic output
- Existing `tool_platform.core.Gateway` contract preserved
- Tests for allow/deny, malformed arguments and configuration
- Agent development instructions: [AGENTS.md](AGENTS.md)

## Prerequisites

Python 3.11+ and Git. The MCP Python SDK is an optional dependency, installed by the `mcp` extra. No Docker, database, paid API key or network access is required for the current tools.

## Quick start

```bash
git clone https://github.com/jcastellobranco/mcp-tool-platform.git
cd mcp-tool-platform
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,mcp]'
python -m pytest -q
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` instead of `source`.

By default, **zero tools** are exposed. To explicitly enable both safe local tools:

```bash
export MCP_ALLOWED_SCOPES=text:read,text:hash
python -m tool_platform.mcp_server
```

The server communicates over **stdio**. It is meant to be launched by an MCP client, not opened in a browser. No web endpoint or listening port is created.

## Connect an MCP client

Configure an MCP client that supports launching stdio servers with the equivalent of:

```json
{
  "mcpServers": {
    "portfolio-tools": {
      "command": "/absolute/path/to/mcp-tool-platform/.venv/bin/python",
      "args": ["-m", "tool_platform.mcp_server"],
      "env": {
        "MCP_ALLOWED_SCOPES": "text:read,text:hash"
      }
    }
  }
}
```

This is a **generic example**, not a universal configuration file: each client has its own settings schema. Use the absolute Python path for your operating system.

The MCP client will discover `word_count(text)` and `sha256_text(text)`. To restrict tools, remove one scope from the environment variable.

## Run the core gateway without MCP

```python
from tool_platform.core import Principal
from tool_platform.catalog import execute

principal = Principal("local-demo", frozenset({"text:read"}))
print(execute(principal, "word_count", {"text": "hello from MCP"}))
# {"words": 3}
```

Unauthorized calls raise `PermissionError`, unknown tools raise `KeyError`, and invalid arguments raise `ValueError`.

## Commands

```bash
# Tests
python -m pytest -q

# Start the local MCP stdio server with one tool
MCP_ALLOWED_SCOPES=text:read python -m tool_platform.mcp_server

# Update an existing checkout
git pull origin main
python -m pip install -e '.[dev,mcp]'
python -m pytest -q
```

## Security and limitations

- `MCP_ALLOWED_SCOPES` is a **trusted server-process setting**, not authenticated end-user authorization.
- Anyone who can communicate with this local process can use its enabled tools. Do not expose the server to untrusted users.
- Tool outputs are data, not trusted instructions.
- No shell, file access, arbitrary HTTP fetching or code execution tools are available.
- No audit database, per-user tenant identity, approvals, quotas, retries or network MCP transport yet.
- Tests added to the repository must still be executed in an actual Python environment; code publication alone does not verify runtime behavior.

See [architecture and security boundaries](docs/ARCHITECTURE.md) and [source-level agent instructions](src/AGENTS.md).

## Next steps

1. Add authenticated network MCP transport with per-user/tenant permissions.
2. Persist redacted tool-call audit events and correlate with agent run IDs.
3. Introduce per-tool approval and idempotent side-effect policies.
4. Integrate authorized tool calling with Multi-Agent Orchestration and ATLAS.
