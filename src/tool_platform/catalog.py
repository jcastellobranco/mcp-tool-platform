"""Bounded, side-effect-free tools on top of the existing scope gateway."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .core import Gateway, Principal, Tool


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    scope: str
    input_schema: dict[str, Any]


SPECS = (
    ToolSpec("word_count", "Count words in a bounded text.", "text:read",
             {"type": "object", "properties": {"text": {"type": "string", "maxLength": 10000}},
              "required": ["text"], "additionalProperties": False}),
    ToolSpec("sha256_text", "Compute the SHA-256 digest of a bounded text.", "text:hash",
             {"type": "object", "properties": {"text": {"type": "string", "maxLength": 10000}},
              "required": ["text"], "additionalProperties": False}),
)


def _text(arguments: dict) -> str:
    if not isinstance(arguments, dict) or set(arguments) != {"text"}:
        raise ValueError("Exactly one 'text' argument is required")
    value = arguments["text"]
    if not isinstance(value, str) or len(value) > 10000:
        raise ValueError("'text' must be a string of at most 10000 characters")
    return value


def create_gateway() -> Gateway:
    gateway = Gateway()
    gateway.register(Tool("word_count", "text:read",
                          lambda arguments: {"words": len(_text(arguments).split())}))
    gateway.register(Tool("sha256_text", "text:hash",
                          lambda arguments: {"sha256": hashlib.sha256(_text(arguments).encode("utf-8")).hexdigest()}))
    return gateway


def visible_tools(principal: Principal) -> list[ToolSpec]:
    return [spec for spec in SPECS if spec.scope in principal.scopes]


def execute(principal: Principal, name: str, arguments: dict) -> dict:
    """Authorization is enforced by Gateway.execute on every invocation."""
    return create_gateway().execute(principal, name, arguments)
