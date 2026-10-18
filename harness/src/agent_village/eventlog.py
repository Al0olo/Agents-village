"""Append-only, hash-chained event log stored as JSONL.

Every perception, message, model call and payment is an event. Each event carries a
monotonic id and the SHA-256 of its canonical form, which includes the previous event's
hash, so editing, deleting or reordering any line breaks the chain on load. Dropping the
tail leaves a valid chain, so callers compare ``head`` against a recorded value.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GENESIS = "0" * 64


class LogCorruptError(Exception):
    """The log on disk is malformed or its hash chain does not verify."""


@dataclass(frozen=True)
class LogEvent:
    id: int
    kind: str
    writer: str
    payload: Mapping[str, Any]
    prev: str
    hash: str


def canonical_hash(value: Any) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _digest(id: int, kind: str, writer: str, payload: Mapping[str, Any], prev: str) -> str:
    return canonical_hash(
        {"id": id, "kind": kind, "writer": writer, "payload": payload, "prev": prev}
    )


def _normalise(payload: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload, allow_nan=False))


class EventLog:
    """A single-writer log backed by one JSONL file, verified when opened."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._events: list[LogEvent] = []
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        text = self._path.read_text(encoding="utf-8")
        if text and not text.endswith("\n"):
            raise LogCorruptError("final line is incomplete")
        prev = GENESIS
        for number, line in enumerate(text.splitlines()):
            try:
                record = json.loads(line)
                event = LogEvent(**record)
            except (ValueError, TypeError) as exc:
                raise LogCorruptError(f"line {number}: unreadable record") from exc
            expected = _digest(event.id, event.kind, event.writer, event.payload, prev)
            if event.id != number or event.prev != prev or event.hash != expected:
                raise LogCorruptError(f"line {number}: hash chain broken")
            self._events.append(event)
            prev = event.hash

    @property
    def head(self) -> str:
        return self._events[-1].hash if self._events else GENESIS

    def append(self, kind: str, writer: str, payload: Mapping[str, Any]) -> LogEvent:
        if not kind or not writer:
            raise ValueError("kind and writer must be non-empty")
        body = _normalise(payload)
        number = len(self._events)
        prev = self.head
        event = LogEvent(
            number, kind, writer, body, prev, _digest(number, kind, writer, body, prev)
        )
        line = json.dumps(event.__dict__, sort_keys=True, ensure_ascii=False) + "\n"
        with self._path.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        self._events.append(event)
        return event

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[LogEvent]:
        return iter(self._events)

    def __getitem__(self, index: int) -> LogEvent:
        return self._events[index]
