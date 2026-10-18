"""Village state and a deterministic wake scheduler.

Time is a tick counter that only the village advances. A citizen with no pending wake is
never returned, so sleeping costs nothing. At most ``max_awake`` citizens are awake at
once; when more are due, the oldest requests go first and ties are broken by the injected
random generator, so a seed fixes the order. Every state change is an event in the log.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from agent_village.eventlog import EventLog

WRITER = "village"


class SimClock:
    def __init__(self, now: int = 0) -> None:
        self.now = now

    def advance(self) -> int:
        self.now += 1
        return self.now


@dataclass(frozen=True)
class VillageState:
    tick: int
    citizens: tuple[str, ...]
    awake: tuple[str, ...]
    pending: tuple[tuple[str, int, str], ...]
    """Wake requests as ``(citizen, tick, reason)``, sorted by citizen."""


class Village:
    def __init__(self, log: EventLog, clock: SimClock, rng: random.Random, max_awake: int) -> None:
        if max_awake < 1:
            raise ValueError("max_awake must be at least 1")
        if len(log):
            raise ValueError("the log must be empty")
        self._log = log
        self._clock = clock
        self._rng = rng
        self._max_awake = max_awake
        self._citizens: set[str] = set()
        self._awake: set[str] = set()
        self._pending: dict[str, tuple[int, str]] = {}

    def add_citizen(self, name: str) -> None:
        if not name or name in self._citizens:
            raise ValueError(f"invalid or duplicate citizen {name!r}")
        self._log.append("born", WRITER, {"citizen": name})
        self._citizens.add(name)

    def request_wake(self, citizen: str, at: int, reason: str) -> None:
        self._require(citizen)
        if at < self._clock.now:
            raise ValueError("cannot request a wake in the past")
        self._log.append("wake_requested", WRITER, {"citizen": citizen, "at": at, "reason": reason})
        held = self._pending.get(citizen)
        if held is None or at < held[0]:
            self._pending[citizen] = (at, reason)

    def sleep(self, citizen: str, until: int | None = None) -> None:
        self._require(citizen)
        if citizen not in self._awake:
            raise ValueError(f"{citizen} is not awake")
        if until is not None and until < self._clock.now:
            raise ValueError("cannot sleep until a past tick")
        self._log.append("slept", WRITER, {"citizen": citizen})
        self._awake.remove(citizen)
        if until is not None:
            self.request_wake(citizen, until, "timer")

    def step(self) -> tuple[str, ...]:
        tick = self._clock.advance()
        self._log.append("tick", WRITER, {"tick": tick})
        due = sorted(
            c for c, (at, _) in self._pending.items() if at <= tick and c not in self._awake
        )
        ranked = sorted((self._pending[c][0], self._rng.random(), c) for c in due)
        free = max(self._max_awake - len(self._awake), 0)
        chosen = tuple(c for _, _, c in ranked[:free])
        for citizen in chosen:
            _, reason = self._pending.pop(citizen)
            self._awake.add(citizen)
            self._log.append("woke", WRITER, {"citizen": citizen, "reason": reason, "tick": tick})
        return chosen

    def state(self) -> VillageState:
        return VillageState(
            tick=self._clock.now,
            citizens=tuple(sorted(self._citizens)),
            awake=tuple(sorted(self._awake)),
            pending=tuple((c, at, reason) for c, (at, reason) in sorted(self._pending.items())),
        )

    def _require(self, citizen: str) -> None:
        if citizen not in self._citizens:
            raise KeyError(citizen)
