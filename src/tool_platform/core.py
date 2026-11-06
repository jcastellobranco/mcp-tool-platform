from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: frozenset[str]

@dataclass(frozen=True)
class Tool:
    name: str
    scope: str
    handler: Callable[[dict], dict]

class Gateway:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ValueError("Duplicate tool")
        self._tools[tool.name] = tool

    def execute(self, principal: Principal, name: str, arguments: dict):
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError("Unknown tool")
        if tool.scope not in principal.scopes:
            raise PermissionError("Insufficient scope")
        return tool.handler(arguments)

def default_gateway():
    gateway = Gateway()
    gateway.register(Tool("word_count", "text:read", lambda a: {"words": len(str(a.get("text", "")).split())}))
    return gateway
