import pytest
from tool_platform.core import default_gateway, Principal
def test_scope_enforced():
    gateway=default_gateway()
    with pytest.raises(PermissionError):
        gateway.execute(Principal("user",frozenset()),"word_count",{"text":"hello"})
    assert gateway.execute(Principal("user",frozenset({"text:read"})),"word_count",{"text":"hello world"})["words"]==2
