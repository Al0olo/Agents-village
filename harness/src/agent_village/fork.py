"""Snapshots and forks of a village at a tick boundary.

A fork is a new log holding a verified prefix of the base log, plus a village rebuilt by
folding that prefix. The only state outside the log is the random generator, so a
snapshot is the log position, its head hash and the generator's state. Arms differ only in
what the caller passes to ``fork``: the memory policy, the prompt and the backend.
"""

from __future__ import annotations

import json
import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_village.eventlog import EventLog
from agent_village.memory import Memory, Policy, Tier
from agent_village.messages import Messenger
from agent_village.model import Backend, Model
from agent_village.prompts import Prompt
from agent_village.runner import LoopConfig, Runner, Spec
from agent_village.village import SimClock, Village


@dataclass(frozen=True)
class Snapshot:
    events: int
    head: str
    rng_state: tuple

    def to_json(self) -> str:
        version, internal, gauss = self.rng_state
        return json.dumps(
            {
                "events": self.events,
                "head": self.head,
                "rng_state": [version, list(internal), gauss],
            }
        )

    @classmethod
    def from_json(cls, text: str) -> Snapshot:
        try:
            data = json.loads(text)
            events, head = data["events"], data["head"]
            version, internal, gauss = data["rng_state"]
            state = (version, tuple(internal), gauss)
            random.Random().setstate(state)
        except (ValueError, KeyError, TypeError):
            raise ValueError("malformed snapshot") from None
        valid_events = isinstance(events, int) and not isinstance(events, bool) and events >= 0
        if not valid_events or not isinstance(head, str) or not head:
            raise ValueError("malformed snapshot")
        return cls(events, head, state)


@dataclass(frozen=True)
class World:
    log: EventLog
    village: Village
    memory: Memory
    messenger: Messenger
    runner: Runner

    def snapshot(self) -> Snapshot:
        if self.village.state().awake:
            raise ValueError("snapshots are taken between ticks")
        return Snapshot(len(self.log), self.log.head, self.village.rng_state())

    def state(self) -> dict[str, Any]:
        """Everything that must match between a base and its forks, for comparison."""
        village = self.village.state()
        memory = tuple(self.memory.entries(Tier.SHARED)) + tuple(
            entry
            for name in village.citizens
            for tier in (Tier.CORE, Tier.RECALL)
            for entry in self.memory.entries(tier, name)
        )
        return {
            "village": village,
            "rng": self.village.rng_state(),
            "cursors": self.runner.cursors(),
            "memory": memory,
            "events": len(self.log),
            "head": self.log.head,
        }


def build(
    log: EventLog,
    rng: random.Random,
    backend: Backend,
    policy: Policy,
    prompt: Prompt,
    specs: Sequence[Spec],
    max_awake: int,
    config: LoopConfig | None = None,
) -> World:
    village = Village(log, SimClock(), rng, max_awake)
    memory = Memory(log, policy)
    messenger = Messenger(log)
    runner = Runner(village, log, memory, messenger, Model(backend, log), specs, prompt, config)
    return World(log, village, memory, messenger, runner)


def fork(
    snapshot: Snapshot,
    source: EventLog,
    dest: Path | str,
    backend: Backend,
    policy: Policy,
    prompt: Prompt,
    specs: Sequence[Spec],
    max_awake: int,
    config: LoopConfig | None = None,
) -> World:
    if source.head_at(snapshot.events) != snapshot.head:
        raise ValueError("the source log does not contain this snapshot")
    log = source.fork(dest, snapshot.events)
    rng = random.Random()
    rng.setstate(snapshot.rng_state)
    try:
        return build(log, rng, backend, policy, prompt, specs, max_awake, config)
    except Exception:
        Path(dest).unlink()
        raise
