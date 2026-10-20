import pytest
from villages import NAMES, gossip

from agent_village.arms import (
    CORROBORATED,
    KERNEL_ADMISSION,
    NO_DEFENSE,
    PROMPT_DEFENSE,
    STANCE_PRESERVING,
    random_block_arm,
)
from agent_village.block import BlockConfig, run_block
from agent_village.consolidation import CONSOLIDATION
from agent_village.eventlog import EventLog
from agent_village.facts import generate, utility_facts
from agent_village.launch import RunConfig
from agent_village.model import FakeBackend, ModelError
from agent_village.probes import PROBE_ROUND
from agent_village.runner import LoopConfig, Spec

SPECS = tuple(Spec(n, "fake/model") for n in NAMES)
RUN = RunConfig(SPECS, 3, LoopConfig(max_steps=2))
ELDERS = ("ada", "bo")


def config(**over):
    base = {
        "seed": 1,
        "block": 0,
        "run": RUN,
        "elders": ELDERS,
        "arms": (NO_DEFENSE, KERNEL_ADMISSION),
        "base_ticks": 3,
        "day_ticks": 4,
        "days": 3,
    }
    base.update(over)
    return BlockConfig(**base)


def go(tmp_path, **over):
    return run_block(config(**over), lambda: FakeBackend(gossip), tmp_path / "block")


def rounds_of(log):
    return [(e.id, e.payload["questions"]) for e in log if e.kind == PROBE_ROUND]


def test_every_arm_gets_a_log_and_the_base_log_is_kept(tmp_path):
    result = go(tmp_path)
    assert sorted(result.logs) == ["A", "D"]
    for name, path in result.logs.items():
        assert path == tmp_path / "block" / f"{name}.jsonl" and path.exists()
    assert result.base_log == tmp_path / "block" / "base.jsonl"


def test_the_base_village_announces_runs_plants_and_forks_the_arms(tmp_path):
    result = go(tmp_path)
    base = EventLog(result.base_log)
    kinds = [e.kind for e in base]
    assert kinds.count("plant") == 12
    assert [e.payload["tick"] for e in base if e.kind == "tick"] == [1, 2, 3]
    for name in result.logs:
        log = EventLog(result.logs[name])
        assert log.head_at(result.snapshot.events) == result.snapshot.head
        assert [e.kind for e in log][result.snapshot.events] == "launch"


def test_the_arms_run_the_days_in_lockstep_with_a_probe_round_at_the_end_of_each(tmp_path):
    result = go(tmp_path)
    for path in result.logs.values():
        log = EventLog(path)
        ticks = [e.payload["tick"] for e in log if e.kind == "tick"]
        assert ticks[-1] == 3 + 4 * 3
        rounds = rounds_of(log)
        assert len(rounds) == 3
        at = []
        for index, _ in rounds:
            at.append(max(e.payload["tick"] for e in log if e.kind == "tick" and e.id < index))
        assert at == [3 + 4, 3 + 8, 3 + 12]


def test_interim_rounds_ask_only_the_facts_and_the_last_adds_the_awareness_funnel(tmp_path):
    result = go(tmp_path)
    log = EventLog(next(iter(result.logs.values())))
    kinds = [[q["kind"] for q in questions] for _, questions in rounds_of(log)]
    assert set(kinds[0]) == set(kinds[1]) == {"fact", "utility"}
    assert kinds[2].count("awareness") == 3 and len(kinds[2]) == len(kinds[0]) + 3
    asked = [q["key"] for q in rounds_of(log)[0][1]]
    expected = [f.id for f in generate(1, 0)] + [f.id for f in utility_facts(1, 0)]
    assert asked == expected


def test_the_same_seed_gives_the_same_block(tmp_path):
    first = go(tmp_path / "one")
    second = go(tmp_path / "two")
    for name in first.logs:
        assert EventLog(first.logs[name]).head == EventLog(second.logs[name]).head


def test_a_different_block_plants_different_facts(tmp_path):
    first = go(tmp_path / "one", block=0)
    second = go(tmp_path / "two", block=1)
    a = {e.payload["entity"] for e in EventLog(first.base_log) if e.kind == "plant"}
    b = {e.payload["entity"] for e in EventLog(second.base_log) if e.kind == "plant"}
    assert a != b


def test_the_colluding_variant_is_planted_when_asked(tmp_path):
    result = go(tmp_path, colluding=True)
    markers = [e for e in EventLog(result.base_log) if e.kind == "plant"]
    assert all(m.payload["colluding"] for m in markers)


def test_any_arm_can_run_in_the_block_including_the_random_block_and_the_exploratory_arm(tmp_path):
    arms = (NO_DEFENSE, PROMPT_DEFENSE, KERNEL_ADMISSION, random_block_arm(0.5, "s"), CORROBORATED)
    result = go(tmp_path, arms=arms, days=1)
    assert sorted(result.logs) == ["A", "B", "D", "E", "G"]
    launches = {
        n: next(e for e in EventLog(p) if e.kind == "launch") for n, p in result.logs.items()
    }
    assert launches["E"].payload["settings"] == {"rate": 0.5, "salt": "s"}
    assert launches["B"].payload["prompt_version"] == "anchor-scrutiny-1a"


def test_a_single_day_has_one_full_round_and_no_interim_round(tmp_path):
    result = go(tmp_path, days=1)
    log = EventLog(next(iter(result.logs.values())))
    assert len(rounds_of(log)) == 1
    assert any(q["kind"] == "awareness" for q in rounds_of(log)[0][1])


def test_a_block_config_is_validated():
    for bad in (
        {"elders": ("ada", "ghost")},
        {"arms": (NO_DEFENSE, NO_DEFENSE)},
        {"arms": ()},
        {"days": 0},
        {"day_ticks": 0},
        {"base_ticks": -1},
    ):
        with pytest.raises(ValueError):
            config(**bad)


def test_a_model_failure_stops_the_block_and_is_not_swallowed(tmp_path):
    class Fails:
        calls = 0

        def complete(self, request):
            Fails.calls += 1
            if Fails.calls > 40:
                raise ModelError("down")
            return FakeBackend(gossip).complete(request)

    with pytest.raises(ModelError):
        run_block(config(), lambda: Fails(), tmp_path / "block")


def markers(log, kind):
    return [(i, e) for i, e in enumerate(log) if e.kind == kind]


def test_every_arm_reviews_after_each_day_but_the_last_with_its_own_review_prompt(tmp_path):
    result = go(tmp_path, arms=(NO_DEFENSE, STANCE_PRESERVING, KERNEL_ADMISSION))
    for name, arm in (("A", NO_DEFENSE), ("C", STANCE_PRESERVING), ("D", KERNEL_ADMISSION)):
        log = EventLog(result.logs[name])
        reviews = markers(log, CONSOLIDATION)
        assert len(reviews) == 2
        assert {e.payload["prompt_hash"] for _, e in reviews} == {arm.review.hash}
        rounds = markers(log, PROBE_ROUND)
        ticks = [i for i, e in enumerate(log) if e.kind == "tick"]
        for day, (at, _) in enumerate(reviews):
            assert rounds[day][0] < at < rounds[day + 1][0]
            assert ticks[(day + 1) * 4 - 1] < rounds[day][0]
        assert len([e for e in log if e.kind == "review"]) == 2 * len(NAMES)


def test_a_block_can_run_without_the_review_pass(tmp_path):
    result = go(tmp_path, consolidate=False)
    for path in result.logs.values():
        assert markers(EventLog(path), CONSOLIDATION) == []


def test_a_one_day_block_has_nothing_to_review(tmp_path):
    result = go(tmp_path, days=1)
    for path in result.logs.values():
        assert markers(EventLog(path), CONSOLIDATION) == []
