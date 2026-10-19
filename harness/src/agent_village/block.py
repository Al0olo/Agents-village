"""Run one block of the RQ1 design: a base village, planting, forked arms, probes.

A block is the paired unit. The base village runs without defense (ADR-0003) with the
elders announced, ten facts and two single-witness facts are planted between ticks, and
every arm forks from that snapshot and runs in lockstep for a number of simulated days.
At the end of each day every arm answers the fact and utility questions; after the last day
it answers them again with the awareness funnel (ADR-0008). The judge runs afterwards, on
the finished logs, so a failed block leaves no codes to mix in.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from agent_village.arms import BASE, Arm
from agent_village.eventlog import EventLog
from agent_village.facts import generate, utility_facts
from agent_village.fork import Snapshot, World, build
from agent_village.launch import RunConfig, launch
from agent_village.model import Backend
from agent_village.planting import Roster, announce, make_plan, plant
from agent_village.probes import Question, questions, run_round


@dataclass(frozen=True)
class BlockConfig:
    seed: int
    block: int
    run: RunConfig
    elders: tuple[str, ...]
    arms: Sequence[Arm]
    base_ticks: int = 4
    day_ticks: int = 12
    days: int = 3
    colluding: bool = False

    def __post_init__(self) -> None:
        names = [arm.name for arm in self.arms]
        if not self.arms or len(set(names)) != len(names):
            raise ValueError("arms must be non-empty with unique names")
        if self.days < 1 or self.day_ticks < 1 or self.base_ticks < 0:
            raise ValueError("a block needs at least one day of at least one tick")
        if not set(self.elders) <= {s.name for s in self.run.specs}:
            raise ValueError("the elders must be citizens")


@dataclass(frozen=True)
class BlockResult:
    base_log: Path
    logs: dict[str, Path]
    snapshot: Snapshot


def run_block(
    config: BlockConfig, make_backend: Callable[[], Backend], directory: Path | str
) -> BlockResult:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    citizens = tuple(s.name for s in config.run.specs)
    roster = Roster(citizens, config.elders)
    facts = generate(config.seed, config.block) + utility_facts(config.seed, config.block)
    plan = make_plan(facts, roster, config.seed, config.block, config.colluding)

    base_log = directory / "base.jsonl"
    base = build(
        EventLog(base_log),
        random.Random(f"{config.seed}:{config.block}"),
        make_backend(),
        BASE.policy,
        BASE.prompt,
        config.run.specs,
        config.run.max_awake,
        config.run.loop,
    )
    announce(base, roster)
    base.runner.run(config.base_ticks)
    snapshot = plant(base, plan)

    run = launch(snapshot, base.log, directory, list(config.arms), make_backend, config.run)
    for day in range(1, config.days + 1):
        run.run(config.day_ticks)
        final = day == config.days
        _probe(list(run.worlds.values()), questions(facts, awareness=final))
    return BlockResult(
        base_log, {name: directory / f"{name}.jsonl" for name in run.worlds}, snapshot
    )


def _probe(worlds: list[World], asked: Sequence[Question]) -> None:
    with ThreadPoolExecutor(max_workers=len(worlds)) as pool:
        list(pool.map(lambda world: run_round(world, asked), worlds))
