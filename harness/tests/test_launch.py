import dataclasses
import random
import re
import threading

import pytest
from villages import NAMES, drive, gossip, specs

from agent_village.admission import admit
from agent_village.arms import ARMS, BASE, KERNEL_ADMISSION, NO_DEFENSE, Arm
from agent_village.eventlog import EventLog
from agent_village.fork import build
from agent_village.launch import DriftError, Launch, RunConfig, launch
from agent_village.model import FakeBackend, ModelError
from agent_village.prompts import Prompt
from agent_village.runner import LoopConfig

CONFIG = RunConfig(tuple(specs()), 3)


def tick_of(request):
    return int(re.match(r"Tick (\d+)\.", request.messages[1].content).group(1))


class Drifting:
    """Wraps a backend and reports another snapshot or provider from a given tick on."""

    def __init__(self, inner, after=0, model=None, provider=None):
        self.inner, self.after, self.model, self.provider = inner, after, model, provider

    def complete(self, request):
        response = self.inner.complete(request)
        if tick_of(request) >= self.after:
            response = dataclasses.replace(
                response,
                model=self.model or response.model,
                provider=self.provider or response.provider,
            )
        return response


class Failing:
    def __init__(self, inner, at):
        self.inner, self.at = inner, at

    def complete(self, request):
        if tick_of(request) >= self.at:
            raise ModelError("down")
        return self.inner.complete(request)


class Recording:
    def __init__(self, inner, calls, lock):
        self.inner, self.calls, self.lock = inner, calls, lock

    def complete(self, request):
        with self.lock:
            self.calls.append(tick_of(request))
        return self.inner.complete(request)


class Meeting:
    """Blocks the first call until another arm's first call arrives at the same time."""

    def __init__(self, inner, barrier):
        self.inner, self.barrier, self.waited = inner, barrier, False

    def complete(self, request):
        if not self.waited:
            self.waited = True
            self.barrier.wait()
        return self.inner.complete(request)


def feed(*backends):
    queue = iter(backends)
    return lambda: next(queue)


def fake():
    return FakeBackend(gossip)


@pytest.fixture
def base(tmp_path):
    log = EventLog(tmp_path / "base.jsonl")
    world = build(log, random.Random(3), fake(), BASE.policy, BASE.prompt, specs(), 3)
    drive(world, 12)
    return world, world.snapshot()


def start(tmp_path, base, arms=(NO_DEFENSE, KERNEL_ADMISSION), make=fake, config=CONFIG):
    world, snap = base
    return launch(snap, world.log, tmp_path / "arms", arms, make, config)


def events(world, kind):
    return [e for e in world.log if e.kind == kind]


def tick_of_first_call_served_as(world, served):
    tick = 0
    for event in world.log:
        if event.kind == "tick":
            tick = event.payload["tick"]
        elif event.kind == "model_call" and event.payload["model_served"] == served:
            return tick
    return None


def test_every_arm_is_forked_from_the_same_snapshot(tmp_path, base):
    world, snap = base
    run = start(tmp_path, base)
    assert set(run.worlds) == {"A", "D"}
    for w in run.worlds.values():
        assert w.log.head_at(snap.events) == snap.head
        assert w.village.state() == world.village.state()


def test_each_arm_gets_its_own_backend_from_the_same_factory(tmp_path, base):
    made = []

    def make():
        made.append(FakeBackend(gossip))
        return made[-1]

    start(tmp_path, base, make=make)
    assert len(made) == 2 and made[0] is not made[1]


def test_each_log_records_the_launch(tmp_path, base):
    _, snap = base
    run = start(tmp_path, base)
    for name, w in run.worlds.items():
        (marker,) = events(w, "launch")
        assert marker.id == snap.events
        assert marker.payload["arm"] == name
        assert marker.payload["snapshot_head"] == snap.head
        assert marker.payload["config_hash"] == CONFIG.hash
        assert marker.payload["prompt_version"] == ARMS[name].prompt.version
        assert marker.payload["prompt_hash"] == ARMS[name].prompt.hash


def test_the_config_hash_is_shared_and_sensitive_to_every_setting(tmp_path, base):
    a = start(tmp_path, base)
    hashes = {events(w, "launch")[0].payload["config_hash"] for w in a.worlds.values()}
    assert len(hashes) == 1
    variants = [
        RunConfig(tuple(specs()), 4),
        RunConfig(tuple(specs()), 3, LoopConfig(max_steps=2)),
        RunConfig(tuple(specs())[:-1], 3),
        RunConfig(tuple(dataclasses.replace(s, model="other/model") for s in specs()), 3),
    ]
    assert len({v.hash for v in variants} | {CONFIG.hash}) == 5
    assert RunConfig(tuple(reversed(specs())), 3).hash == CONFIG.hash


def test_arms_share_the_log_up_to_the_fork_and_the_launch_marker_is_the_first_difference(
    tmp_path, base
):
    _, snap = base
    run = start(tmp_path, base)
    a, d = run.worlds["A"].log, run.worlds["D"].log
    assert a.head_at(snap.events) == d.head_at(snap.events)
    assert a[snap.events] != d[snap.events]


def test_a_lockstep_run_advances_every_arm_by_the_same_ticks(tmp_path, base):
    run = start(tmp_path, base)
    run.run(5)
    assert {w.village.state().tick for w in run.worlds.values()} == {17}


def test_no_arm_starts_a_tick_before_every_arm_has_finished_the_previous_one(tmp_path, base):
    calls, lock = [], threading.Lock()
    run = start(
        tmp_path,
        base,
        make=lambda: Recording(FakeBackend(gossip), calls, lock),
    )
    run.run(8)
    assert calls and calls == sorted(calls)
    assert set(calls) <= set(range(13, 21))


def test_arms_really_run_at_the_same_time(tmp_path, base):
    barrier = threading.Barrier(2, timeout=5)
    meetings = [Meeting(FakeBackend(gossip), barrier) for _ in range(2)]
    start(tmp_path, base, make=feed(*meetings)).run(6)
    assert all(m.waited for m in meetings)


def test_the_sequential_mode_cannot_meet_the_barrier(tmp_path, base):
    barrier = threading.Barrier(2, timeout=0.5)
    run = start(tmp_path, base, make=lambda: Meeting(FakeBackend(gossip), barrier))
    with pytest.raises(threading.BrokenBarrierError):
        run.run(6, parallel=False)


def test_parallel_and_sequential_runs_give_identical_logs(tmp_path, base):
    world, snap = base
    one = launch(snap, world.log, tmp_path / "one", [NO_DEFENSE, KERNEL_ADMISSION], fake, CONFIG)
    two = launch(snap, world.log, tmp_path / "two", [NO_DEFENSE, KERNEL_ADMISSION], fake, CONFIG)
    one.run(15, parallel=True)
    two.run(15, parallel=False)
    for name in ("A", "D"):
        assert one.worlds[name].log.head == two.worlds[name].log.head
    assert one.worlds["A"].log.head != one.worlds["D"].log.head


def test_arm_order_does_not_change_any_arms_result(tmp_path, base):
    world, snap = base
    one = launch(snap, world.log, tmp_path / "one", [NO_DEFENSE, KERNEL_ADMISSION], fake, CONFIG)
    two = launch(snap, world.log, tmp_path / "two", [KERNEL_ADMISSION, NO_DEFENSE], fake, CONFIG)
    one.run(10)
    two.run(10)
    for name in ("A", "D"):
        assert one.worlds[name].log.head == two.worlds[name].log.head


def test_an_empty_or_duplicated_arm_list_is_refused_without_files(tmp_path, base):
    for arms in ([], [NO_DEFENSE, NO_DEFENSE]):
        with pytest.raises(ValueError):
            start(tmp_path, base, arms=arms)
    assert not (tmp_path / "arms").exists()


def test_a_launch_that_fails_part_way_leaves_no_files(tmp_path, base):
    (tmp_path / "arms").mkdir()
    (tmp_path / "arms" / "D.jsonl").write_text("keep")
    with pytest.raises(FileExistsError):
        start(tmp_path, base)
    assert sorted(p.name for p in (tmp_path / "arms").iterdir()) == ["D.jsonl"]
    assert (tmp_path / "arms" / "D.jsonl").read_text() == "keep"


def test_a_foreign_snapshot_launches_nothing(tmp_path, base):
    other_log = EventLog(tmp_path / "other.jsonl")
    other = build(other_log, random.Random(99), fake(), BASE.policy, BASE.prompt, specs(), 3)
    drive(other, 12)
    with pytest.raises(ValueError):
        launch(base[1], other.log, tmp_path / "arms", [NO_DEFENSE], fake, CONFIG)
    assert not (tmp_path / "arms").exists() or not any((tmp_path / "arms").iterdir())


def test_a_failure_in_one_arm_stops_the_whole_block(tmp_path, base):
    run = start(tmp_path, base, make=feed(fake(), Failing(fake(), at=16)))
    with pytest.raises(ModelError):
        run.run(10)
    ticks = {name: w.village.state().tick for name, w in run.worlds.items()}
    assert ticks["A"] == ticks["D"] and 16 <= ticks["A"] < 22
    with pytest.raises(RuntimeError):
        run.run(1)
    assert {name: w.village.state().tick for name, w in run.worlds.items()} == ticks


def test_no_drift_is_reported_for_a_steady_run(tmp_path, base):
    run = start(tmp_path, base)
    run.run(6)
    assert run.drift() == ()


def test_a_changed_snapshot_mid_run_aborts_the_block_at_that_tick(tmp_path, base):
    run = start(
        tmp_path, base, make=feed(fake(), Drifting(fake(), after=15, model="fake/model-v2"))
    )
    with pytest.raises(DriftError) as error:
        run.run(10)
    first = tick_of_first_call_served_as(run.worlds["D"], "fake/model-v2")
    assert first is not None and first >= 15
    assert {w.village.state().tick for w in run.worlds.values()} == {first}
    (finding,) = error.value.findings
    assert finding.model == "fake/model"
    assert set(finding.observed) == {("fake/model", "fake"), ("fake/model-v2", "fake")}
    with pytest.raises(RuntimeError):
        run.run(1)


def test_a_provider_switch_is_drift_too(tmp_path, base):
    run = start(tmp_path, base, make=feed(fake(), Drifting(fake(), after=14, provider="other")))
    with pytest.raises(DriftError) as error:
        run.run(8)
    assert {p for _, p in error.value.findings[0].observed} == {"fake", "other"}


def test_drift_since_the_base_run_is_caught_on_the_first_call(tmp_path, base):
    run = start(tmp_path, base, make=lambda: Drifting(fake(), model="fake/model-v2"))
    with pytest.raises(DriftError):
        run.run(6)
    first = tick_of_first_call_served_as(run.worlds["A"], "fake/model-v2")
    assert run.worlds["A"].village.state().tick == first


def test_drift_can_be_tolerated_and_still_reported(tmp_path, base):
    run = start(tmp_path, base, make=feed(fake(), Drifting(fake(), after=15, provider="other")))
    run.run(8, abort_on_drift=False)
    assert run.worlds["D"].village.state().tick == 20
    (finding,) = run.drift()
    assert {provider for _, provider in finding.observed} == {"fake", "other"}


def test_every_requested_model_is_checked_separately(tmp_path):
    mixed = RunConfig(
        tuple(dataclasses.replace(s, model=f"fake/model-{i % 2}") for i, s in enumerate(specs())),
        3,
    )
    other = build(
        EventLog(tmp_path / "mixed.jsonl"),
        random.Random(3),
        fake(),
        BASE.policy,
        BASE.prompt,
        list(mixed.specs),
        3,
    )
    drive(other, 6)
    run = launch(other.snapshot(), other.log, tmp_path / "arms", [NO_DEFENSE], fake, mixed)
    run.run(6)
    assert run.drift() == ()


def test_the_run_is_deterministic_per_seed(tmp_path):
    def heads(seed, name):
        log = EventLog(tmp_path / f"{name}.jsonl")
        w = build(log, random.Random(seed), fake(), BASE.policy, BASE.prompt, specs(), 3)
        drive(w, 8)
        r = launch(
            w.snapshot(), w.log, tmp_path / name, [NO_DEFENSE, KERNEL_ADMISSION], fake, CONFIG
        )
        r.run(8)
        return {n: x.log.head for n, x in r.worlds.items()}

    assert heads(1, "a") == heads(1, "b")
    assert heads(1, "c") != heads(2, "d")


def test_each_arm_runs_with_its_own_prompt_and_policy(tmp_path, base):
    _, snap = base
    brief = Arm("B", admit, Prompt("brief-1", "Be brief."))
    run = start(tmp_path, base, arms=[NO_DEFENSE, brief])
    run.run(4)
    for name, version in (("A", "baseline-1"), ("B", "brief-1")):
        after = [e for e in events(run.worlds[name], "step") if e.id >= snap.events]
        assert after and {e.payload["prompt_version"] for e in after} == {version}


def test_the_launch_object_exposes_its_arms_in_order(tmp_path, base):
    run = start(tmp_path, base, arms=[KERNEL_ADMISSION, NO_DEFENSE])
    assert isinstance(run, Launch)
    assert list(run.worlds) == ["D", "A"]
    assert set(NAMES) == set(run.worlds["A"].village.state().citizens)
