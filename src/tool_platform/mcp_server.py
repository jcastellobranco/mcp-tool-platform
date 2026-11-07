"""Local stdio MCP server with explicit process-level scope allowlist."""
from __future__ import annotations

import os

from .core import Principal
from .catalog import execute, visible_tools


def configured_principal() -> Principal:
    raw = os.getenv("MCP_ALLOWED_SCOPES", "")
    allowed = {"text:read", "text:hash"}
    scopes = frozenset(scope.strip() for scope in raw.split(",") if scope.strip())
    if not scopes.issubset(allowed):
        raise ValueError("Unknown configured scope")
    return Principal(subject="local-mcp-process", scopes=scopes)


def build_mcp_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install -e '.[mcp]'") from exc

    principal = configured_principal()
    server = FastMCP("mcp-tool-platform")
    names = {spec.name for spec in visible_tools(principal)}

    if "word_count" in names:
        @server.tool()
        def word_count(text: str) -> dict:
            """Count words in text (max 10000 characters)."""
            return execute(principal, "word_count", {"text": text})

    if "sha256_text" in names:
        @server.tool()
        def sha256_text(text: str) -> dict:
            """Compute SHA-256 of text (max 10000 characters)."""
            return execute(principal, "sha256_text", {"text": text})

    return server


def main():
    build_mcp_server().run(transport="stdio")


if __name__ == "__main__":
    main()
