import hashlib
import pytest
from tool_platform.core import Principal
from tool_platform.catalog import execute, visible_tools
from tool_platform.mcp_server import configured_principal


def principal(*scopes):
    return Principal(subject="test", scopes=frozenset(scopes))


def test_allowlisted_tools():
    assert execute(principal("text:read"), "word_count", {"text": "two words"}) == {"words": 2}
    assert execute(principal("text:hash"), "sha256_text", {"text": "abc"}) == {
        "sha256": hashlib.sha256(b"abc").hexdigest()
    }


def test_default_deny():
    with pytest.raises(PermissionError):
        execute(principal(), "word_count", {"text": "denied"})
    with pytest.raises(KeyError):
        execute(principal("text:read"), "unknown", {"text": "denied"})


def test_argument_bounds_and_types():
    for arguments in ({"text": 123}, {"text": "x" * 10001}, {}, {"text": "ok", "extra": 1}):
        with pytest.raises(ValueError):
            execute(principal("text:read"), "word_count", arguments)


def test_discovery_respects_scope():
    assert [spec.name for spec in visible_tools(principal("text:hash"))] == ["sha256_text"]
    assert visible_tools(principal()) == []


def test_configured_scopes_default_deny(monkeypatch):
    monkeypatch.delenv("MCP_ALLOWED_SCOPES", raising=False)
    assert configured_principal().scopes == frozenset()
    monkeypatch.setenv("MCP_ALLOWED_SCOPES", "text:read,text:hash")
    assert configured_principal().scopes == frozenset({"text:read", "text:hash"})
    monkeypatch.setenv("MCP_ALLOWED_SCOPES", "admin")
    with pytest.raises(ValueError):
        configured_principal()
