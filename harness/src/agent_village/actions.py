"""Parse a model reply into one citizen action.

The reply must contain a JSON object with an ``action`` key. Prose and code fences around
it are tolerated, extra keys are ignored, and only the first such object is used.
Anything else raises ``ActionError`` with a reason the citizen may be shown.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypeGuard

from agent_village.admission import Kind
from agent_village.memory import Tier


class ActionError(ValueError):
    """The reply is not a valid action."""


@dataclass(frozen=True)
class Say:
    to: str
    text: str


@dataclass(frozen=True)
class Forward:
    to: str
    told: str


@dataclass(frozen=True)
class Remember:
    text: str
    kind: Kind
    cites: tuple[str, ...]
    tier: Tier


@dataclass(frozen=True)
class Sleep:
    ticks: int


Action = Say | Forward | Remember | Sleep

MAX_NOTES = 8
"""The most notes one review may write, so a reply cannot write without bound."""


@dataclass(frozen=True)
class Note:
    text: str
    cites: tuple[str, ...]


def parse(reply: str) -> Action:
    data = _first_action_object(reply)
    name = data["action"]
    if name == "say":
        return Say(_text(data, "to"), _text(data, "text"))
    if name == "forward":
        return Forward(_text(data, "to"), _id(data.get("told"), "told"))
    if name == "remember":
        return Remember(
            _text(data, "text"),
            _choice(data, "kind", Kind),
            _ids(data.get("cites")),
            _choice(data, "tier", Tier, allowed=(Tier.CORE, Tier.SHARED)),
        )
    if name == "sleep":
        ticks = data.get("ticks")
        if not _is_int(ticks) or ticks < 1:
            raise ActionError("ticks must be a whole number of at least 1")
        return Sleep(ticks)
    raise ActionError(f"unknown action {name!r}")


def parse_notes(reply: str) -> tuple[Note, ...]:
    """The notes of a review reply: the first JSON object with a ``notes`` list, capped."""
    data = _first_object(reply, "notes")
    items = data["notes"]
    if not isinstance(items, list):
        raise ActionError("notes must be a list")
    notes = []
    for item in items[:MAX_NOTES]:
        if not isinstance(item, dict):
            raise ActionError("each note must be an object with text and cites")
        notes.append(Note(_text(item, "text"), _ids(item.get("cites"))))
    return tuple(notes)


def _first_action_object(reply: str) -> dict[str, Any]:
    return _first_object(reply, "action")


def _first_object(reply: str, key: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    index = reply.find("{")
    while index != -1:
        try:
            value, _ = decoder.raw_decode(reply, index)
        except ValueError:
            value = None
        if isinstance(value, dict) and key in value:
            return value
        index = reply.find("{", index + 1)
    raise ActionError(f"no JSON {key} found")


def _is_int(value: Any) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


def _text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ActionError(f"{key} must be non-empty text")
    return value


def _id(value: Any, key: str) -> str:
    if _is_int(value) and value >= 0:
        return str(value)
    if isinstance(value, str) and value.isdigit():
        return value
    raise ActionError(f"{key} must be an event number")


def _ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ActionError("cites must be a list of event numbers")
    return tuple(_id(item, "cites") for item in value)


def _choice(
    data: dict[str, Any], key: str, enum: Any, allowed: tuple[Any, ...] | None = None
) -> Any:
    try:
        choice = enum(data.get(key))
    except ValueError:
        raise ActionError(f"{key} is not one of the allowed values") from None
    if allowed is not None and choice not in allowed:
        raise ActionError(f"{key} is not one of the allowed values")
    return choice
