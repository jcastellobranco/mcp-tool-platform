from dataclasses import dataclass
from typing import Callable
from time import perf_counter
import logging
import hashlib
import json

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
    def __init__(self, audit_sink=None):
        self._tools: dict[str, Tool] = {}
        self._audit_sink = audit_sink

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
        started = perf_counter()
        outcome = "error"
        try:
            result = tool.handler(arguments)
            outcome = "ok"
            return result
        finally:
            # No raw tool arguments, results, tokens or secrets are logged.
            if self._audit_sink is not None:
                self._audit_sink({"subject_hash": hashlib.sha256(principal.subject.encode()).hexdigest()[:16],
                                  "tool": tool.name, "outcome": outcome,
                                  "duration_ms": round((perf_counter() - started) * 1000, 2)})

def default_gateway():
    gateway = Gateway()
    gateway.register(Tool("word_count", "text:read", lambda a: {"words": len(str(a.get("text", "")).split())}))
    return gateway
