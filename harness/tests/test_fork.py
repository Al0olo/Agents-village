import dataclasses
import json
import random

import pytest
from villages import NAMES, behave

from agent_village.admission import Admission, admit
from agent_village.arms import admit_all
from agent_village.eventlog import EventLog
from agent_village.fork import Snapshot, build, fork
from agent_village.model import FakeBackend, RecordedBackend
from agent_village.prompts import BASELINE, Prompt
from agent_village.runner import Spec


def specs():
    return [Spec(n, "fake/model") for n in NAMES]


def base(tmp_path, ticks, seed=0, name="base.jsonl", policy=admit):
    log = EventLog(tmp_path / name)
    world = build(log, random.Random(seed), FakeBackend(behave), policy, BASELINE, specs(), 3)
    world.runner.run(ticks)
    return world


def arm(tmp_path, snapshot, source, name, policy=admit, prompt=BASELINE, backend=None):
    return fork(
        snapshot,
        source,
        tmp_path / name,
        backend or FakeBackend(behave),
        policy,
        prompt,
        specs(),
        3,
    )


def lines(path):
    return path.read_bytes().splitlines(keepends=True)


def first_difference(a, b):
    return next(i for i, (x, y) in enumerate(zip(a.log, b.log)) if x != y)


def test_a_fresh_world_runs_like_a_hand_built_one(tmp_path):
    world = base(tmp_path, 5)
    assert world.village.state().tick == 5
    assert world.village.state().citizens == tuple(sorted(NAMES))
    assert set(world.state()) == {"village", "rng", "cursors", "memory", "events", "head"}


def test_snapshot_records_the_log_position_and_round_trips_through_json(tmp_path):
    world = base(tmp_path, 6)
    snap = world.snapshot()
    assert (snap.events, snap.head) == (len(world.log), world.log.head)
    assert Snapshot.from_json(snap.to_json()) == snap


def valid_json():
    return json.loads(Snapshot(3, "h" * 64, random.Random(0).getstate()).to_json())


@pytest.mark.parametrize(
    "field,value",
    [
        ("events", -1),
        ("events", True),
        ("events", "3"),
        ("events", 1.5),
        ("head", 5),
        ("head", ""),
        ("rng_state", "x"),
        ("rng_state", [3, [1, 2], None]),
        ("rng_state", [3]),
    ],
)
def test_a_snapshot_with_one_bad_field_is_rejected(field, value):
    Snapshot.from_json(json.dumps(valid_json()))
    data = valid_json()
    data[field] = value
    with pytest.raises(ValueError):
        Snapshot.from_json(json.dumps(data))


@pytest.mark.parametrize("missing", ["events", "head", "rng_state"])
def test_a_snapshot_with_a_missing_field_is_rejected(missing):
    data = valid_json()
    del data[missing]
    with pytest.raises(ValueError):
        Snapshot.from_json(json.dumps(data))


@pytest.mark.parametrize("text", ["", "[]", "null", "{"])
def test_text_that_is_not_a_snapshot_is_rejected(text):
    with pytest.raises(ValueError):
        Snapshot.from_json(text)


def test_snapshots_are_only_taken_between_ticks(tmp_path):
    world = base(tmp_path, 3)
    world.village.request_wake("ada", world.village.state().tick + 1, "test")
    world.village.step()
    assert world.village.state().awake
    with pytest.raises(ValueError):
        world.snapshot()


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("ticks", [0, 1, 5, 17, 40])
def test_a_fork_starts_in_exactly_the_state_of_the_base(tmp_path, ticks, seed):
    world = base(tmp_path, ticks, seed=seed)
    snap = world.snapshot()
    forked = arm(tmp_path, snap, world.log, "fork.jsonl")
    assert forked.state() == world.state()
    assert forked.runner.cursors() == world.runner.cursors()
    assert (forked.runner.cursors() != {}) == (ticks > 0)
    assert forked.log.head == snap.head
    assert lines(tmp_path / "fork.jsonl") == lines(tmp_path / "base.jsonl")[: snap.events]


@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("ticks", [0, 5, 17, 40])
def test_a_fork_continues_exactly_like_a_base_that_never_forked(tmp_path, ticks, seed):
    world = base(tmp_path, ticks, seed=seed)
    forked = arm(tmp_path, world.snapshot(), world.log, "fork.jsonl")
    world.runner.run(30)
    forked.runner.run(30)
    assert forked.log.head == world.log.head
    assert forked.state() == world.state()


def test_two_forks_of_the_same_arm_stay_identical(tmp_path):
    world = base(tmp_path, 20)
    snap = world.snapshot()
    a = arm(tmp_path, snap, world.log, "a.jsonl")
    b = arm(tmp_path, snap, world.log, "b.jsonl")
    a.runner.run(40)
    b.runner.run(40)
    assert a.log.head == b.log.head
    assert a.state() == b.state()


def test_forking_works_after_the_base_has_moved_on(tmp_path):
    world = base(tmp_path, 10)
    snap = world.snapshot()
    world.runner.run(20)
    forked = arm(tmp_path, snap, world.log, "fork.jsonl")
    assert len(forked.log) == snap.events
    forked.runner.run(20)
    assert forked.log.head == world.log.head


def test_arms_with_different_policies_share_the_prefix_and_diverge_after_it(tmp_path):
    world = base(tmp_path, 20)
    snap = world.snapshot()
    a = arm(tmp_path, snap, world.log, "a.jsonl", policy=admit)
    b = arm(tmp_path, snap, world.log, "b.jsonl", policy=admit_all)
    assert a.state() == b.state()
    a.runner.run(40)
    b.runner.run(40)
    assert a.log.head != b.log.head
    assert lines(tmp_path / "a.jsonl")[: snap.events] == lines(tmp_path / "b.jsonl")[: snap.events]
    assert first_difference(a, b) >= snap.events


def test_arms_with_different_prompts_diverge_at_the_first_step(tmp_path):
    world = base(tmp_path, 20)
    snap = world.snapshot()
    a = arm(tmp_path, snap, world.log, "a.jsonl")
    b = arm(tmp_path, snap, world.log, "b.jsonl", prompt=Prompt("other-1", "Be brief."))
    a.runner.run(5)
    b.runner.run(5)
    index = first_difference(a, b)
    assert index >= snap.events
    assert a.log[index].kind == b.log[index].kind == "step"
    assert b.log[index].payload["prompt_version"] == "other-1"


def test_the_policy_only_applies_to_writes_after_the_fork(tmp_path):
    world = base(tmp_path, 30)
    snap = world.snapshot()
    before = world.state()["memory"]
    forked = arm(tmp_path, snap, world.log, "fork.jsonl", policy=admit_all)
    assert forked.state()["memory"] == before
    assert any(e.admission is Admission.HEARSAY for e in before)


def test_forks_write_only_to_their_own_files(tmp_path):
    world = base(tmp_path, 10)
    snap = world.snapshot()
    frozen = (tmp_path / "base.jsonl").read_bytes()
    a = arm(tmp_path, snap, world.log, "a.jsonl")
    b = arm(tmp_path, snap, world.log, "b.jsonl")
    a.runner.run(10)
    assert (tmp_path / "base.jsonl").read_bytes() == frozen
    assert len(EventLog(tmp_path / "b.jsonl")) == snap.events
    assert len(a.log) > len(b.log)


def test_the_rng_state_is_part_of_the_snapshot(tmp_path):
    world = base(tmp_path, 12)
    snap = world.snapshot()
    right = arm(tmp_path, snap, world.log, "right.jsonl")
    wrong = arm(
        tmp_path,
        dataclasses.replace(snap, rng_state=random.Random(999).getstate()),
        world.log,
        "wrong.jsonl",
    )
    right.runner.run(40)
    wrong.runner.run(40)
    assert right.log.head != wrong.log.head


def test_a_fork_can_replay_recorded_outputs_to_the_same_result(tmp_path):
    world = base(tmp_path, 10)
    snap = world.snapshot()
    world.runner.run(20)
    replay = arm(
        tmp_path, snap, world.log, "replay.jsonl", backend=RecordedBackend.from_log(world.log)
    )
    replay.runner.run(20)
    assert replay.log.head == world.log.head


def test_a_snapshot_from_another_history_is_refused_without_creating_a_file(tmp_path):
    world = base(tmp_path, 10, seed=0)
    other = base(tmp_path, 10, seed=1, name="other.jsonl")
    with pytest.raises(ValueError):
        arm(tmp_path, world.snapshot(), other.log, "fork.jsonl")
    assert not (tmp_path / "fork.jsonl").exists()


def test_a_source_shorter_than_the_snapshot_is_refused(tmp_path):
    world = base(tmp_path, 10)
    snap = world.snapshot()
    short = world.log.fork(tmp_path / "short.jsonl", snap.events - 3)
    with pytest.raises(ValueError):
        arm(tmp_path, snap, short, "fork.jsonl")
    assert not (tmp_path / "fork.jsonl").exists()


def test_a_tampered_head_is_refused(tmp_path):
    world = base(tmp_path, 10)
    bad = dataclasses.replace(world.snapshot(), head="0" * 63 + "1")
    with pytest.raises(ValueError):
        arm(tmp_path, bad, world.log, "fork.jsonl")


def test_an_existing_destination_is_never_overwritten(tmp_path):
    world = base(tmp_path, 5)
    (tmp_path / "fork.jsonl").write_text("keep")
    with pytest.raises(FileExistsError):
        arm(tmp_path, world.snapshot(), world.log, "fork.jsonl")
    assert (tmp_path / "fork.jsonl").read_text() == "keep"


def test_a_fork_must_use_the_same_citizens(tmp_path):
    world = base(tmp_path, 5)
    with pytest.raises(ValueError):
        fork(
            world.snapshot(),
            world.log,
            tmp_path / "fork.jsonl",
            FakeBackend(behave),
            admit,
            BASELINE,
            [Spec("ada", "fake/model")],
            3,
        )
    assert not (tmp_path / "fork.jsonl").exists()
