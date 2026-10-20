"""Audit replay and counterfactual branches from a recorded log.

An audit re-drives a recorded run: every tick runs the real runner against the recorded
model outputs, environment events (``saw``, ``did``) and the ``launch`` marker are
re-appended, and each event produced is compared with the original. The first difference
is reported. A branch replays the original up to a tick boundary to recover the exact
state there, including the random generator, then continues under a changed arm. It reuses
a recorded output whenever the request is identical and otherwise asks a fresh backend,
counting both.

Replay does not claim bit-for-bit reproducibility of hosted models; it reuses their recorded
outputs. Prompts carry event numbers, so once a branch's numbering differs from the
original's, later requests no longer match and nothing more is reused.
"""

from __future__ import annotations

import random
import tempfile
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from agent_village.arms import Arm
from agent_village.consolidation import CONSOLIDATION, run_consolidation
from agent_village.eventlog import EventLog, LogEvent
from agent_village.fork import Snapshot, World, build, fork
from agent_village.launch import RunConfig
from agent_village.model import Backend, NotRecordedError, RecordedBackend, Request, Response
from agent_village.probes import PROBE_ROUND, Question, run_round
from agent_village.prompts import Prompt

ENVIRONMENT = frozenset({"saw", "heard", "did", "plant"})
INPUTS = ENVIRONMENT | {"launch"}
DRIVEN = ("tick", PROBE_ROUND, CONSOLIDATION)
"""The events that mark a driver action: a replay re-executes it and compares what it wrote."""


@dataclass(frozen=True)
class Divergence:
    index: int
    expected: LogEvent | None
    got: LogEvent | None
    reason: str


@dataclass(frozen=True)
class AuditResult:
    divergence: Divergence | None
    events: int

    @property
    def ok(self) -> bool:
        return self.divergence is None


class ReplayBackend:
    """Replays recorded outputs and, if given one, asks a fresh backend for the rest."""

    def __init__(self, recorded: RecordedBackend, fresh: Backend | None = None) -> None:
        self._recorded = recorded
        self._fresh = fresh
        self.replayed = 0
        self.fresh_requests: list[str] = []

    def complete(self, request: Request) -> Response:
        try:
            response = self._recorded.complete(request)
        except NotRecordedError:
            if self._fresh is None:
                raise
            self.fresh_requests.append(request.hash)
            return self._fresh.complete(request)
        self.replayed += 1
        return response


class Branch:
    def __init__(
        self, world: World, backend: ReplayBackend, steps: deque[LogEvent], review: Prompt
    ) -> None:
        self.world = world
        self.backend = backend
        self._steps = steps
        self._review = review

    def run(self) -> None:
        """Replay the rest of the original's ticks and environment events."""
        while self._steps:
            step = self._steps.popleft()
            if step.kind == "tick":
                self.world.runner.tick()
            elif step.kind == PROBE_ROUND:
                run_round(self.world, _asked(step))
            elif step.kind == CONSOLIDATION:
                run_consolidation(self.world, self._review)
            else:
                self.world.log.append(step.kind, step.writer, step.payload)


def audit(
    original: EventLog,
    dest: Path | str,
    start: int | Snapshot,
    arm: Arm,
    config: RunConfig,
) -> AuditResult:
    """Replay ``original`` into a new log at ``dest``.

    ``start`` is the seed of a run that began from scratch, or the snapshot a launched arm
    was forked from.
    """
    world = _start(original, dest, start, arm, config)
    divergence, _ = _redrive(world, original, arm, config, len(original))
    return AuditResult(divergence, len(world.log))


def branch(
    original: EventLog,
    cut: int,
    dest: Path | str,
    start: int | Snapshot,
    original_arm: Arm,
    new_arm: Arm,
    config: RunConfig,
    fresh: Backend | None = None,
) -> Branch:
    """Continue ``original`` from the tick boundary at event ``cut`` as ``new_arm``."""
    if not 0 <= cut <= len(original):
        raise ValueError(f"the log has {len(original)} events, not {cut}")
    with tempfile.TemporaryDirectory() as scratch:
        world = _start(original, Path(scratch) / "prefix.jsonl", start, original_arm, config)
        divergence, index = _redrive(world, original, original_arm, config, cut)
        if divergence is not None:
            raise ValueError(
                f"the original does not replay up to event {cut}: "
                f"{divergence.reason} (event {divergence.index})"
            )
        if index != cut:
            raise ValueError(f"event {cut} is not between ticks")
        snapshot = world.snapshot()
    backend = ReplayBackend(RecordedBackend.from_log(original, cut), fresh)
    branched = fork(
        snapshot,
        original,
        dest,
        backend,
        new_arm.policy,
        new_arm.prompt,
        config.specs,
        config.max_awake,
        config.loop,
    )
    steps = deque(
        event
        for event in (original[i] for i in range(cut, len(original)))
        if event.kind in ENVIRONMENT | {"tick", PROBE_ROUND, CONSOLIDATION}
    )
    return Branch(branched, backend, steps, new_arm.review)


def _start(
    original: EventLog, dest: Path | str, start: int | Snapshot, arm: Arm, config: RunConfig
) -> World:
    if isinstance(start, Snapshot):
        recorded = RecordedBackend.from_log(original, start.events)
        return fork(
            start,
            original,
            dest,
            recorded,
            arm.policy,
            arm.prompt,
            config.specs,
            config.max_awake,
            config.loop,
        )
    if Path(dest).exists():
        raise FileExistsError(str(dest))
    return build(
        EventLog(dest),
        random.Random(start),
        RecordedBackend.from_log(original),
        arm.policy,
        arm.prompt,
        config.specs,
        config.max_awake,
        config.loop,
    )


def _redrive(
    world: World, original: EventLog, arm: Arm, config: RunConfig, stop: int
) -> tuple[Divergence | None, int]:
    """Re-drive ``world`` through ``original`` until event ``stop``; return where it stopped."""
    log = world.log
    index = len(log)
    prefix = _differ(_events(original, 0, min(index, len(original))), _events(log, 0, index), 0)
    if prefix is not None:
        return prefix, 0
    while index < stop:
        event = original[index]
        if event.kind in DRIVEN:
            if event.kind == CONSOLIDATION and event.payload["prompt_hash"] != arm.review.hash:
                reason = "the recorded review used a different prompt"
                return Divergence(index, event, None, reason), index
            try:
                if event.kind == "tick":
                    world.runner.tick()
                elif event.kind == PROBE_ROUND:
                    run_round(world, _asked(event))
                else:
                    run_consolidation(world, arm.review)
            except NotRecordedError:
                at = len(log)
                earlier = _differ_common(
                    _events(original, index, at), _events(log, index, at), index
                )
                if earlier is not None:
                    return earlier, index
                expected = original[at] if at < len(original) else None
                reason = "the replay asked for a request that was never recorded"
                return Divergence(at, expected, None, reason), index
            end = _segment_end(original, index)
            difference = _differ(
                _events(original, index, end), _events(log, index, len(log)), index
            )
            if difference is not None:
                return difference, index
            index = end
        elif event.kind in INPUTS:
            if event.kind == "launch" and not _launched_as(event, arm, config):
                reason = "the recorded launch used a different arm or configuration"
                return Divergence(index, event, None, reason), index
            log.append(event.kind, event.writer, event.payload)
            index += 1
        else:
            reason = "the event is neither produced by a tick nor an environment input"
            return Divergence(index, event, None, reason), index
    return None, index


def _asked(event: LogEvent) -> list[Question]:
    return [Question(**question) for question in event.payload["questions"]]


def _launched_as(event: LogEvent, arm: Arm, config: RunConfig) -> bool:
    p = event.payload
    return (
        p["arm"] == arm.name
        and p["config_hash"] == config.hash
        and p["prompt_hash"] == arm.prompt.hash
        and p["settings"] == arm.settings
    )


def _segment_end(original: EventLog, index: int) -> int:
    end = index + 1
    while (
        end < len(original)
        and original[end].kind not in DRIVEN
        and original[end].kind not in INPUTS
    ):
        end += 1
    return end


def _events(log: EventLog, start: int, end: int) -> Sequence[LogEvent]:
    return [log[i] for i in range(start, end)]


def _differ_common(
    expected: Sequence[LogEvent], got: Sequence[LogEvent], offset: int
) -> Divergence | None:
    for k, (want, have) in enumerate(zip(expected, got, strict=False)):
        if want != have:
            return Divergence(offset + k, want, have, "the replay produced a different event")
    return None


def _differ(
    expected: Sequence[LogEvent], got: Sequence[LogEvent], offset: int
) -> Divergence | None:
    common = _differ_common(expected, got, offset)
    if common is not None:
        return common
    if len(got) < len(expected):
        return Divergence(offset + len(got), expected[len(got)], None, "the replay stopped early")
    if len(got) > len(expected):
        return Divergence(
            offset + len(expected), None, got[len(expected)], "the replay produced extra events"
        )
    return None
