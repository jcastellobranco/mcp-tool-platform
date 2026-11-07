# Architecture and security boundaries

## Current data flow

```text
Trusted local MCP client
    | stdio (MCP SDK FastMCP)
    v
MCP tool registration (filtered by configured scopes)
    |
    v
Tool catalog -> Gateway.execute -> scope check -> bounded handler
    |
    v
Deterministic JSON result
```

The existing `tool_platform.core` API remains compatible. `catalog.py` adds two strictly bounded, side-effect-free tools. `mcp_server.py` exposes them through the official MCP Python SDK over stdio.

## Security model

- Default scope configuration is empty: no tools are registered.
- A local process operator may explicitly set `MCP_ALLOWED_SCOPES=text:read,text:hash`.
- This is **not** user authentication: every caller able to invoke the local server gets the configured process permissions.
- Gateway checks the required scope again at invocation time.
- Tool argument types and lengths are bounded. No shell, network, filesystem or arbitrary code execution tools are exposed.
- stdio is a local integration boundary, not a secure network multi-tenant deployment.

## Future hardening

1. Authenticated HTTP MCP transport with verified principal and audience-bound tokens.
2. Per-user/tenant scope policy, tool-specific approvals and quotas.
3. Structured audit trail with redaction and correlation IDs.
4. Persistent tool execution records, timeouts, idempotency and safe retry policies.
5. ATLAS and Multi-Agent integration through authenticated service identity.

Do not describe any future items as implemented.
