"""Actual MCP server adapter (requires pip install mcp)."""
from .core import Gateway, Principal, Tool

def build_mcp_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install mcp") from exc

    server = FastMCP("portfolio-tool-server")
    gateway = Gateway()
    gateway.register(Tool("word_count", "text:read", lambda args: {"words": len(args["text"].split())}))

    @server.tool()
    def word_count(text: str) -> int:
        """Count words in user-provided text."""
        # Demo identity only: production servers must validate caller identity.
        principal = Principal("local-demo", frozenset({"text:read"}))
        return gateway.execute(principal, "word_count", {"text": text})["words"]

    return server

def main():
    build_mcp_server().run()

if __name__ == "__main__":
    main()
