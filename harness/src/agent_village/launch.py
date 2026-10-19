"""Launch every arm of a block from one snapshot and run the arms in lockstep.

All arms get the same ``RunConfig`` and a backend from the same factory, so the arm itself,
its memory policy and prompt, is the only thing that can differ. The arms advance one tick
at a time behind a barrier, concurrently, so a hosted model that changes mid-run changes
for every arm at about the same moment. The launch is all or nothing, and each arm's log
records the arm, the config hash and the snapshot it started from.

A block that fails, or whose models drift, is dead: the experiment excludes it rather than
resumes it. Drift means a requested model that served more than one snapshot or provider
across all calls in all arms, base run included. Provider fallbacks are off in the backend.
"""

from __future__ import annotations

import dataclasses
from collections import defaultdict
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path

from agent_village.arms import Arm
from agent_village.eventlog import EventLog, canonical_hash
from agent_village.fork import Snapshot, World, fork
from agent_village.model import Backend
from agent_village.runner import LoopConfig, Spec

LAUNCHER = "launcher"


@dataclass(frozen=True)
class RunConfig:
    specs: tuple[Spec, ...]
    max_awake: int
    loop: LoopConfig = field(default_factory=LoopConfig)

    @property
    def hash(self) -> str:
        return canonical_hash(
            {
                "specs": sorted([s.name, s.model] for s in self.specs),
                "max_awake": self.max_awake,
                "loop": dataclasses.asdict(self.loop),
            }
        )


@dataclass(frozen=True)
class Drift:
    model: str
    observed: tuple[tuple[str, str], ...]
    """The distinct ``(served model, provider)`` pairs seen for the requested model."""


class DriftError(Exception):
    def __init__(self, findings: tuple[Drift, ...]) -> None:
        super().__init__(f"{len(findings)} requested model(s) changed snapshot or provider")
        self.findings = findings


def launch(
    snapshot: Snapshot,
    source: EventLog,
    directory: Path | str,
    arms: Sequence[Arm],
    make_backend: Callable[[], Backend],
    config: RunConfig,
) -> Launch:
    names = [arm.name for arm in arms]
    if not arms or len(set(names)) != len(names):
        raise ValueError("arms must be non-empty with unique names")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    worlds: dict[str, World] = {}
    try:
        for arm in arms:
            path = directory / f"{arm.name}.jsonl"
            world = fork(
                snapshot,
                source,
                path,
                make_backend(),
                arm.policy,
                arm.prompt,
                config.specs,
                config.max_awake,
                config.loop,
            )
            created.append(path)
            world.log.append(
                "launch",
                LAUNCHER,
                {
                    "arm": arm.name,
                    "snapshot_head": snapshot.head,
                    "config_hash": config.hash,
                    "prompt_version": arm.prompt.version,
                    "prompt_hash": arm.prompt.hash,
                    "settings": arm.settings,
                },
            )
            worlds[arm.name] = world
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return Launch(worlds)


class Launch:
    def __init__(self, worlds: dict[str, World]) -> None:
        self.worlds = worlds
        self._failed = False
        self._scanned = dict.fromkeys(worlds, 0)
        self._served: dict[str, set[tuple[str, str]]] = defaultdict(set)
        self._scan()

    def run(self, ticks: int, abort_on_drift: bool = True, parallel: bool = True) -> None:
        workers = len(self.worlds) if parallel else 1
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for _ in range(ticks):
                self._tick(pool, abort_on_drift)

    def drift(self) -> tuple[Drift, ...]:
        return tuple(
            Drift(model, tuple(sorted(pairs)))
            for model, pairs in sorted(self._served.items())
            if len(pairs) > 1
        )

    def _tick(self, pool: ThreadPoolExecutor, abort_on_drift: bool) -> None:
        if self._failed:
            raise RuntimeError("this block has failed and is excluded")
        futures = [pool.submit(world.runner.tick) for world in self.worlds.values()]
        wait(futures)
        errors = [error for f in futures if (error := f.exception()) is not None]
        if errors:
            self._failed = True
            raise errors[0]
        self._scan()
        found = self.drift()
        if found and abort_on_drift:
            self._failed = True
            raise DriftError(found)

    def _scan(self) -> None:
        for name, world in self.worlds.items():
            for index in range(self._scanned[name], len(world.log)):
                event = world.log[index]
                if event.kind == "model_call":
                    p = event.payload
                    self._served[p["model_requested"]].add((p["model_served"], p["provider"]))
            self._scanned[name] = len(world.log)
