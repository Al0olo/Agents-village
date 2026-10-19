"""Announce who the village elders are, then plant facts as first-hand observations.

Status is made real by a notice every citizen sees: the elders are named. A high-status
fact is held by elders and a low-status fact by everyone else. A holder gets an ordinary
``saw`` event, which is first-hand evidence for that citizen and nothing else, so the
kernel treats a planted fact like any other: a true fact has two independent holders and
a false fact has one, or two in the colluding variant. A utility fact is true and has one
holder, whatever the variant. A ``plant`` event records the plan
for the analysis; citizens never see it.

Both functions append only ``saw`` and ``plant`` events between ticks, which audit replay
reproduces.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from agent_village.facts import Fact, Level
from agent_village.fork import ENVIRONMENT, Snapshot, World


@dataclass(frozen=True)
class Roster:
    citizens: tuple[str, ...]
    elders: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(set(self.citizens)) != len(self.citizens):
            raise ValueError("citizens must be distinct")
        if len(set(self.elders)) != len(self.elders) or not set(self.elders) <= set(self.citizens):
            raise ValueError("elders must be distinct citizens")
        if len(self.elders) < 2 or len(self.others) < 2:
            raise ValueError("there must be at least two elders and two other citizens")

    @property
    def others(self) -> tuple[str, ...]:
        return tuple(c for c in self.citizens if c not in self.elders)

    @property
    def notice(self) -> str:
        *rest, last = self.elders
        names = f"{', '.join(rest)} and {last}"
        return f"The elders of the village are {names}."


@dataclass(frozen=True)
class Planting:
    fact: Fact
    holders: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    plantings: tuple[Planting, ...]
    colluding: bool


def make_plan(
    facts: tuple[Fact, ...], roster: Roster, seed: int, block: int, colluding: bool = False
) -> Plan:
    rng = random.Random(f"{seed}:{block}:holders")
    pools = {Level.HIGH: list(roster.elders), Level.LOW: list(roster.others)}
    for pool in pools.values():
        rng.shuffle(pool)
    cursor = {Level.HIGH: 0, Level.LOW: 0}
    plantings = []
    for fact in facts:
        pool, start = pools[fact.status], cursor[fact.status]
        count = 2 if (fact.truth or colluding) and not fact.utility else 1
        holders = tuple(pool[(start + i) % len(pool)] for i in range(count))
        cursor[fact.status] += count
        plantings.append(Planting(fact, holders))
    return Plan(tuple(plantings), colluding)


def announce(world: World, roster: Roster) -> None:
    state = world.village.state()
    if set(roster.citizens) != set(state.citizens):
        raise ValueError("the roster must name exactly the citizens in the village")
    if state.awake:
        raise ValueError("events are appended between ticks")
    for name in sorted(roster.citizens):
        world.log.append("saw", name, {"text": roster.notice})


def plant(world: World, plan: Plan) -> Snapshot:
    if world.village.state().awake:
        raise ValueError("events are appended between ticks")
    if any(event.kind == "plant" for event in world.log):
        raise ValueError("this village has already been planted")
    for planting in plan.plantings:
        fact = planting.fact
        world.log.append(
            "plant",
            ENVIRONMENT,
            {
                "fact": fact.id,
                "template": fact.template,
                "entity": fact.entity,
                "text": fact.text,
                "answer": fact.answer,
                "truth": fact.truth,
                "plausibility": fact.plausibility.value,
                "status": fact.status.value,
                "holders": list(planting.holders),
                "colluding": plan.colluding,
                "utility": fact.utility,
            },
        )
        for holder in planting.holders:
            world.log.append("saw", holder, {"text": fact.observation})
    return world.snapshot()
