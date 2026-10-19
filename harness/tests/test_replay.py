import dataclasses
import random
from dataclasses import dataclass
from pathlib import Path

import pytest
from villages import drive, gossip, specs

from agent_village.admission import admit
from agent_village.arms import (
    BASE,
    KERNEL_ADMISSION,
    NO_DEFENSE,
    Arm,
    admit_all,
    random_block_arm,
)
from agent_village.eventlog import EventLog
from agent_village.fork import Snapshot, World, build
from agent_village.launch import RunConfig, launch
from agent_village.model import FakeBackend, NotRecordedError, RecordedBackend
from agent_village.prompts import BASELINE, Prompt
from agent_village.replay import AuditResult, Branch, ReplayBackend, audit, branch
from agent_village.runner import LoopConfig

CONFIG = RunConfig(tuple(specs()), 3)
SEED = 5


@dataclass
class Recorded:
    world: World
    path: Path
    arm_snapshot: Snapshot
    arms: dict[str, EventLog]
    arm_paths: dict[str, Path]


@pytest.fixture(scope="module")
def recorded(tmp_path_factory):
    root = tmp_path_factory.mktemp("recorded")
    world = build(
        EventLog(root / "base.jsonl"),
        random.Random(SEED),
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        specs(),
        3,
    )
    drive(world, 16)
    other = build(
        EventLog(root / "other.jsonl"),
        random.Random(7),
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        specs(),
        3,
    )
    drive(other, 12)
    snapshot = other.snapshot()
    run = launch(
        snapshot,
        other.log,
        root / "arms",
        [NO_DEFENSE, KERNEL_ADMISSION],
        lambda: FakeBackend(gossip),
        CONFIG,
    )
    run.run(8)
    return Recorded(
        world,
        root / "base.jsonl",
        snapshot,
        {n: w.log for n, w in run.worlds.items()},
        {n: root / "arms" / f"{n}.jsonl" for n in run.worlds},
    )


def run_audit(recorded, tmp_path, name="replay.jsonl", start=SEED, arm=BASE, config=CONFIG):
    return audit(recorded.world.log, tmp_path / name, start, arm, config)


def first_difference(a, b):
    return next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)


def rebuilt(source, path, edit):
    entries = edit([(e.kind, e.writer, dict(e.payload)) for e in source])
    log = EventLog(path)
    for kind, writer, payload in entries:
        log.append(kind, writer, payload)
    return log


def index_of(log, kind, nth=0):
    return [i for i, e in enumerate(log) if e.kind == kind][nth]


def test_a_recorded_run_replays_to_the_same_bytes(recorded, tmp_path):
    result = run_audit(recorded, tmp_path)
    assert isinstance(result, AuditResult)
    assert result.ok and result.divergence is None
    assert result.events == len(recorded.world.log)
    assert (tmp_path / "replay.jsonl").read_bytes() == recorded.path.read_bytes()


def test_the_original_is_left_untouched(recorded, tmp_path):
    before = recorded.path.read_bytes()
    run_audit(recorded, tmp_path)
    assert recorded.path.read_bytes() == before


def test_the_replay_needs_a_fresh_destination(recorded, tmp_path):
    (tmp_path / "replay.jsonl").write_text("keep")
    with pytest.raises(FileExistsError):
        run_audit(recorded, tmp_path)
    assert (tmp_path / "replay.jsonl").read_text() == "keep"


@pytest.mark.parametrize("name,arm", [("A", NO_DEFENSE), ("D", KERNEL_ADMISSION)])
def test_a_launched_arm_replays_from_its_snapshot(recorded, tmp_path, name, arm):
    log = recorded.arms[name]
    result = audit(log, tmp_path / "arm.jsonl", recorded.arm_snapshot, arm, CONFIG)
    assert result.ok and result.events == len(log)
    assert (tmp_path / "arm.jsonl").read_bytes() == recorded.arm_paths[name].read_bytes()


def test_a_wrong_seed_diverges_at_the_first_differing_event(recorded, tmp_path):
    result = run_audit(recorded, tmp_path, start=SEED + 1)
    assert not result.ok
    d = result.divergence
    replay = EventLog(tmp_path / "replay.jsonl")
    assert d.index == first_difference(recorded.world.log, replay)
    assert d.expected == recorded.world.log[d.index] and d.got == replay[d.index]


def test_a_wrong_policy_diverges_at_the_first_claim(recorded, tmp_path):
    impostor = Arm("D", admit_all, BASELINE)
    result = audit(
        recorded.arms["D"], tmp_path / "arm.jsonl", recorded.arm_snapshot, impostor, CONFIG
    )
    d = result.divergence
    assert d is not None
    assert d.expected.kind == d.got.kind == "claim"
    assert d.expected.payload["admission"] != d.got.payload["admission"]


def test_the_wrong_arm_is_caught_at_the_launch_event(recorded, tmp_path):
    result = audit(
        recorded.arms["D"], tmp_path / "arm.jsonl", recorded.arm_snapshot, NO_DEFENSE, CONFIG
    )
    assert result.divergence.index == recorded.arm_snapshot.events
    assert result.divergence.expected.kind == "launch"
    assert "launch" in result.divergence.reason


def test_a_different_config_is_caught_at_the_launch_event(recorded, tmp_path):
    other = RunConfig(tuple(specs()), 4)
    result = audit(
        recorded.arms["D"], tmp_path / "arm.jsonl", recorded.arm_snapshot, KERNEL_ADMISSION, other
    )
    assert result.divergence.expected.kind == "launch"


def test_a_different_prompt_is_caught_at_the_launch_event(recorded, tmp_path):
    arm = Arm("D", admit, Prompt("other-1", "Be brief."))
    result = audit(recorded.arms["D"], tmp_path / "arm.jsonl", recorded.arm_snapshot, arm, CONFIG)
    assert result.divergence.index == recorded.arm_snapshot.events
    assert result.divergence.expected.kind == "launch"


def test_different_citizens_diverge_in_the_setup(recorded, tmp_path):
    fewer = RunConfig(tuple(specs())[:-1], 3)
    result = run_audit(recorded, tmp_path, config=fewer)
    assert result.divergence is not None and result.divergence.index < 2 * len(specs())


def test_a_renamed_citizen_is_caught_in_the_setup_not_later(recorded, tmp_path):
    names = [
        dataclasses.replace(s, name="zed" if i == 0 else s.name) for i, s in enumerate(specs())
    ]
    result = run_audit(recorded, tmp_path, config=RunConfig(tuple(names), 3))
    assert result.divergence.index < 2 * len(specs())
    assert result.divergence.expected.kind == "born"


def test_a_different_prompt_diverges_at_the_first_step(recorded, tmp_path):
    arm = Arm("A", admit_all, Prompt("other-1", "Be brief."))
    result = run_audit(recorded, tmp_path, arm=arm)
    assert result.divergence.index == index_of(recorded.world.log, "step")
    assert result.divergence.expected.kind == "step"


def test_a_request_that_was_never_recorded_is_reported(recorded, tmp_path):
    result = run_audit(
        recorded, tmp_path, config=RunConfig(tuple(specs()), 3, LoopConfig(memory_limit=1))
    )
    d = result.divergence
    assert d is not None and d.got is None
    assert d.expected.kind == "model_call"
    assert "never recorded" in d.reason


def test_a_missing_trailing_event_is_reported(recorded, tmp_path):
    assert recorded.world.log[len(recorded.world.log) - 1].kind != "tick"
    short = rebuilt(recorded.world.log, tmp_path / "short.jsonl", lambda es: es[:-1])
    result = audit(short, tmp_path / "replay.jsonl", SEED, BASE, CONFIG)
    d = result.divergence
    assert d.index == len(short) and d.expected is None and d.got is not None


def test_an_extra_event_inside_a_tick_is_reported(recorded, tmp_path):
    at = index_of(recorded.world.log, "tick", 3)

    def insert(entries):
        return entries[:at] + [("note", "village", {})] + entries[at:]

    padded = rebuilt(recorded.world.log, tmp_path / "padded.jsonl", insert)
    result = audit(padded, tmp_path / "replay.jsonl", SEED, BASE, CONFIG)
    d = result.divergence
    assert d.index == at and d.expected.kind == "note" and d.got is None


def test_a_driver_action_before_the_first_tick_is_not_replayable(tmp_path):
    world = build(
        EventLog(tmp_path / "o.jsonl"),
        random.Random(1),
        FakeBackend(gossip),
        admit,
        BASELINE,
        specs(),
        3,
    )
    world.village.request_wake("ada", 1, "driver")
    world.runner.run(2)
    result = audit(world.log, tmp_path / "r.jsonl", 1, Arm("D", admit, BASELINE), CONFIG)
    assert "neither" in result.divergence.reason
    assert result.divergence.expected.kind == "wake_requested"


def test_a_driver_action_after_a_tick_is_reported_as_unexplained(tmp_path):
    world = build(
        EventLog(tmp_path / "o.jsonl"),
        random.Random(1),
        FakeBackend(gossip),
        admit,
        BASELINE,
        specs(),
        3,
    )
    world.runner.tick()
    world.village.request_wake("ada", 5, "driver")
    world.runner.run(2)
    result = audit(world.log, tmp_path / "r.jsonl", 1, Arm("D", admit, BASELINE), CONFIG)
    assert result.divergence.expected.kind == "wake_requested"
    assert result.divergence.got is None


def test_the_replay_backend_counts_what_it_replays_and_what_it_asks_for_fresh(tmp_path):
    from agent_village.model import Message, Model, Request

    def ask(text):
        return Request("m", (Message("user", text),), 5)

    log = EventLog(tmp_path / "v.jsonl")
    Model(FakeBackend(), log).complete("ada", ask("known"))
    backend = ReplayBackend(RecordedBackend.from_log(log), FakeBackend(lambda r: "fresh"))
    assert backend.complete(ask("known")).text != "fresh"
    assert backend.complete(ask("new")).text == "fresh"
    assert backend.replayed == 1
    assert backend.fresh_requests == [ask("new").hash]


def test_the_replay_backend_without_a_fresh_backend_is_strict(tmp_path):
    from agent_village.model import Message, Request

    backend = ReplayBackend(RecordedBackend.from_log(EventLog(tmp_path / "v.jsonl")))
    with pytest.raises(NotRecordedError):
        backend.complete(Request("m", (Message("user", "x"),), 5))
    assert backend.replayed == 0 and backend.fresh_requests == []


def boundaries(log):
    return [i for i, e in enumerate(log) if e.kind == "tick"]


def make_branch(recorded, tmp_path, cut, new_arm=BASE, fresh=None, name="branch.jsonl", start=SEED):
    return branch(recorded.world.log, cut, tmp_path / name, start, BASE, new_arm, CONFIG, fresh)


def test_a_branch_without_changes_reproduces_the_original_exactly(recorded, tmp_path):
    log = recorded.world.log
    cut = boundaries(log)[6]
    b = make_branch(recorded, tmp_path, cut)
    assert isinstance(b, Branch)
    assert b.world.log.head_at(cut) == log.head_at(cut)
    b.run()
    assert b.world.log.head == log.head
    assert (tmp_path / "branch.jsonl").read_bytes() == recorded.path.read_bytes()
    calls_after = sum(1 for i in range(cut, len(log)) if log[i].kind == "model_call")
    assert b.backend.replayed == calls_after and b.backend.fresh_requests == []


def test_branches_can_start_before_an_input_and_at_the_very_end(recorded, tmp_path):
    log = recorded.world.log
    for n, cut in enumerate((index_of(log, "saw", 2), len(log))):
        b = make_branch(recorded, tmp_path, cut, name=f"b{n}.jsonl")
        b.run()
        assert b.world.log.head == log.head


def test_a_changed_branch_shares_the_prefix_then_diverges_with_fresh_calls(recorded, tmp_path):
    log = recorded.world.log
    cut = boundaries(log)[6]
    b = make_branch(recorded, tmp_path, cut, KERNEL_ADMISSION, FakeBackend(gossip))
    b.run()
    branch_log = b.world.log
    assert branch_log.head != log.head
    assert branch_log.head_at(cut) == log.head_at(cut)
    assert first_difference(log, branch_log) >= cut
    calls = sum(1 for i in range(cut, len(branch_log)) if branch_log[i].kind == "model_call")
    assert b.backend.replayed > 0 and b.backend.fresh_requests
    assert b.backend.replayed + len(b.backend.fresh_requests) == calls


def test_without_a_fresh_backend_a_changed_branch_stops_at_the_first_new_request(
    recorded, tmp_path
):
    cut = boundaries(recorded.world.log)[6]
    b = make_branch(recorded, tmp_path, cut, KERNEL_ADMISSION)
    with pytest.raises(NotRecordedError):
        b.run()


def test_a_branch_can_be_driven_by_hand_to_try_an_intervention(recorded, tmp_path):
    log = recorded.world.log
    cut = boundaries(log)[6]
    b = make_branch(recorded, tmp_path, cut, BASE, FakeBackend(gossip))
    for _ in range(6):
        b.world.runner.tick()
    assert b.backend.replayed > 0 and b.backend.fresh_requests
    assert b.world.village.state().tick == log[cut].payload["tick"] + 5


def test_running_a_branch_twice_does_nothing_the_second_time(recorded, tmp_path):
    cut = boundaries(recorded.world.log)[6]
    b = make_branch(recorded, tmp_path, cut)
    b.run()
    head = b.world.log.head
    b.run()
    assert b.world.log.head == head


@pytest.mark.parametrize("what", ["inside a tick", "inside the setup", "past the end", "negative"])
def test_a_cut_must_fall_between_ticks(recorded, tmp_path, what):
    log = recorded.world.log
    cut = {
        "inside a tick": index_of(log, "step"),
        "inside the setup": 3,
        "past the end": len(log) + 1,
        "negative": -1,
    }[what]
    with pytest.raises(ValueError):
        make_branch(recorded, tmp_path, cut)
    assert not (tmp_path / "branch.jsonl").exists()


def test_a_branch_refuses_when_the_original_does_not_replay(recorded, tmp_path):
    cut = boundaries(recorded.world.log)[6]
    with pytest.raises(ValueError, match="replay"):
        make_branch(recorded, tmp_path, cut, start=SEED + 1)


def test_a_branch_of_a_launched_arm_starts_from_its_snapshot(recorded, tmp_path):
    log = recorded.arms["D"]
    cut = [i for i in boundaries(log) if i > recorded.arm_snapshot.events][3]
    b = branch(
        log,
        cut,
        tmp_path / "b.jsonl",
        recorded.arm_snapshot,
        KERNEL_ADMISSION,
        KERNEL_ADMISSION,
        CONFIG,
    )
    b.run()
    assert b.world.log.head == log.head
    with pytest.raises(ValueError):
        branch(
            log,
            recorded.arm_snapshot.events - 1,
            tmp_path / "early.jsonl",
            recorded.arm_snapshot,
            KERNEL_ADMISSION,
            KERNEL_ADMISSION,
            CONFIG,
        )


def test_a_branch_does_not_overwrite_an_existing_file(recorded, tmp_path):
    (tmp_path / "branch.jsonl").write_text("keep")
    with pytest.raises(FileExistsError):
        make_branch(recorded, tmp_path, boundaries(recorded.world.log)[6])
    assert (tmp_path / "branch.jsonl").read_text() == "keep"


def test_a_branch_leaves_only_its_own_file_in_the_destination_folder(recorded, tmp_path):
    folder = tmp_path / "out"
    folder.mkdir()
    branch(
        recorded.world.log,
        boundaries(recorded.world.log)[6],
        folder / "b.jsonl",
        SEED,
        BASE,
        BASE,
        CONFIG,
    ).run()
    assert [p.name for p in folder.iterdir()] == ["b.jsonl"]


def test_a_different_policy_setting_is_caught_at_the_launch_event(tmp_path):
    world = build(
        EventLog(tmp_path / "base.jsonl"),
        random.Random(SEED),
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        specs(),
        3,
    )
    drive(world, 6)
    snapshot = world.snapshot()
    arm = random_block_arm(0.5, "s")
    run = launch(snapshot, world.log, tmp_path / "arms", [arm], lambda: FakeBackend(gossip), CONFIG)
    run.run(4)
    other = random_block_arm(0.4, "s")
    log = run.worlds["E"].log
    result = audit(log, tmp_path / "arm.jsonl", snapshot, other, CONFIG)
    assert result.divergence.index == snapshot.events
    assert result.divergence.expected.kind == "launch"
    assert audit(log, tmp_path / "again.jsonl", snapshot, arm, CONFIG).ok
