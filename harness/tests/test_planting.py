import random
from collections import Counter

import pytest
from villages import NAMES, gossip

from agent_village.admission import Admission, Kind, admit, admit_corroborated
from agent_village.arms import BASE, KERNEL_ADMISSION, NO_DEFENSE
from agent_village.eventlog import EventLog
from agent_village.facts import Level, generate, utility_facts
from agent_village.fork import build
from agent_village.launch import RunConfig, launch
from agent_village.memory import Memory, Tier
from agent_village.messages import Messenger
from agent_village.model import FakeBackend
from agent_village.planting import Plan, Roster, announce, make_plan, plant
from agent_village.replay import audit
from agent_village.runner import Spec

ELDERS = ("ada", "bo")
ROSTER = Roster(NAMES, ELDERS)
SPECS = [Spec(n, "fake/model") for n in NAMES]
CONFIG = RunConfig(tuple(SPECS), 3)


def fresh(tmp_path, seed=1, name="v.jsonl"):
    return build(
        EventLog(tmp_path / name),
        random.Random(seed),
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        SPECS,
        3,
    )


def by_status(plan, level):
    return [p for p in plan.plantings if p.fact.status is level]


def test_the_roster_names_the_elders_and_everyone_else():
    assert ROSTER.others == tuple(n for n in NAMES if n not in ELDERS)
    assert ROSTER.notice == "The elders of the village are ada and bo."
    three = Roster(NAMES, ("ada", "bo", "cy"))
    assert three.notice == "The elders of the village are ada, bo and cy."


@pytest.mark.parametrize(
    "citizens,elders",
    [
        (NAMES, ("ada",)),
        (NAMES, ("ada", "ghost")),
        (NAMES, ("ada", "ada")),
        (NAMES, NAMES[:-1]),
        (("ada", "ada", "bo", "cy", "di"), ("ada", "bo")),
        (("ada", "bo"), ("ada", "bo")),
    ],
)
def test_a_roster_needs_two_elders_and_two_others_among_distinct_citizens(citizens, elders):
    with pytest.raises(ValueError):
        Roster(citizens, elders)


def test_true_facts_have_two_independent_holders_and_false_facts_one():
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    for p in plan.plantings:
        assert len(p.holders) == (2 if p.fact.truth else 1)
        assert len(set(p.holders)) == len(p.holders)


def test_the_colluding_variant_gives_false_facts_two_holders_too():
    plan = make_plan(generate(1, 0), ROSTER, 1, 0, colluding=True)
    assert plan.colluding
    assert all(len(p.holders) == 2 for p in plan.plantings)
    assert not make_plan(generate(1, 0), ROSTER, 1, 0).colluding


def test_the_holders_come_from_the_group_the_fact_calls_for():
    for colluding in (False, True):
        plan = make_plan(generate(2, 1), ROSTER, 2, 1, colluding)
        for p in plan.plantings:
            group = ROSTER.elders if p.fact.status is Level.HIGH else ROSTER.others
            assert set(p.holders) <= set(group)


def test_the_load_is_spread_evenly_across_each_group():
    plan = make_plan(generate(3, 2), ROSTER, 3, 2, colluding=True)
    held = Counter(h for p in by_status(plan, Level.LOW) for h in p.holders)
    load = [held[name] for name in ROSTER.others]
    assert max(load) - min(load) <= 1 and min(load) > 0
    assert set(held) <= set(ROSTER.others)


def test_planning_is_deterministic_and_depends_on_seed_and_block():
    facts = generate(1, 0)
    assert make_plan(facts, ROSTER, 1, 0) == make_plan(facts, ROSTER, 1, 0)
    assert make_plan(facts, ROSTER, 1, 0) != make_plan(facts, ROSTER, 2, 0)
    assert make_plan(facts, ROSTER, 1, 0) != make_plan(facts, ROSTER, 1, 1)


def test_announcing_gives_every_citizen_the_same_first_hand_notice(tmp_path):
    world = fresh(tmp_path)
    announce(world, ROSTER)
    notices = [e for e in world.log if e.kind == "saw"]
    assert sorted(e.writer for e in notices) == sorted(NAMES)
    assert {e.payload["text"] for e in notices} == {ROSTER.notice}


def test_announcing_while_a_citizen_is_awake_is_refused(tmp_path):
    world = fresh(tmp_path)
    world.village.step()
    before = len(world.log)
    with pytest.raises(ValueError):
        announce(world, ROSTER)
    assert len(world.log) == before


def test_the_planting_marker_records_the_colluding_variant(tmp_path):
    world = fresh(tmp_path)
    plant(world, make_plan(generate(1, 0), ROSTER, 1, 0, colluding=True))
    markers = [e for e in world.log if e.kind == "plant"]
    assert markers and all(m.payload["colluding"] is True for m in markers)
    assert all(len(m.payload["holders"]) == 2 for m in markers)


def test_announcing_needs_the_roster_to_match_the_village(tmp_path):
    world = fresh(tmp_path)
    with pytest.raises(ValueError):
        announce(world, Roster(NAMES[:-1], ELDERS))
    assert not [e for e in world.log if e.kind == "saw"]


def test_planting_records_each_fact_then_gives_each_holder_a_first_hand_observation(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    snapshot = plant(world, plan)
    markers = [e for e in world.log if e.kind == "plant"]
    saws = [e for e in world.log if e.kind == "saw"]
    assert len(markers) == 10 and len(saws) == 14
    for p in plan.plantings:
        marker = next(e for e in markers if e.payload["fact"] == p.fact.id)
        assert marker.payload["truth"] is p.fact.truth
        assert marker.payload["holders"] == list(p.holders)
        assert marker.payload["answer"] == p.fact.answer
        assert marker.payload["entity"] == p.fact.entity
        assert marker.payload["colluding"] is False
        for holder in p.holders:
            assert any(e.writer == holder and e.payload["text"] == p.fact.observation for e in saws)
    assert snapshot.events == len(world.log)


def test_nothing_is_given_to_citizens_who_hold_no_fact(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    plant(world, plan)
    holders = {h for p in plan.plantings for h in p.holders}
    saw_writers = {e.writer for e in world.log if e.kind == "saw"}
    assert saw_writers == holders


def test_planting_twice_or_while_a_citizen_is_awake_is_refused(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    plant(world, plan)
    size = len(world.log)
    with pytest.raises(ValueError):
        plant(world, plan)
    assert len(world.log) == size

    other = fresh(tmp_path, name="w.jsonl")
    other.village.step()
    assert other.village.state().awake
    before = len(other.log)
    with pytest.raises(ValueError):
        plant(other, plan)
    assert len(other.log) == before


def test_holders_see_their_observation_and_nobody_else_does(tmp_path):
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    calls = []

    class Spy:
        def complete(self, request):
            calls.append(request)
            return FakeBackend(lambda r: '{"action": "sleep", "ticks": 5}').complete(request)

    spied = build(
        EventLog(tmp_path / "spy.jsonl"),
        random.Random(1),
        Spy(),
        BASE.policy,
        BASE.prompt,
        SPECS,
        3,
    )
    announce(spied, ROSTER)
    plant(spied, plan)
    spied.runner.run(4)
    prompts = {}
    for request in calls:
        name = request.messages[0].content.split(".")[0].removeprefix("You are ")
        prompts.setdefault(name, []).append(request.messages[1].content)
    for p in plan.plantings:
        for name in NAMES:
            seen = any(p.fact.observation in text for text in prompts.get(name, []))
            assert seen == (name in p.holders)
    assert all(ROSTER.notice in texts[0] for texts in prompts.values())


def tell(log, speaker, listener, text):
    return str(Messenger(log).send(speaker, listener, text).told)


def test_a_true_fact_told_by_both_independent_holders_is_admitted_by_the_kernel(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    plant(world, plan)
    true = next(p for p in plan.plantings if p.fact.truth)
    listener = next(n for n in NAMES if n not in true.holders)
    cites = tuple(tell(world.log, h, listener, true.fact.text) for h in true.holders)
    entry = Memory(world.log, admit).write_claim(
        listener, true.fact.text, Kind.TOLD, cites, Tier.SHARED
    )
    assert entry.admission is Admission.FACT


def test_a_false_fact_from_its_single_holder_is_hearsay_under_the_kernel(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    plant(world, plan)
    false = next(p for p in plan.plantings if not p.fact.truth)
    listener = next(n for n in NAMES if n not in false.holders)
    told = tell(world.log, false.holders[0], listener, false.fact.text)
    memory = Memory(world.log, admit)
    one = memory.write_claim(listener, false.fact.text, Kind.TOLD, (told,), Tier.SHARED)
    twice = memory.write_claim(listener, false.fact.text, Kind.TOLD, (told, told), Tier.SHARED)
    assert one.admission is twice.admission is Admission.HEARSAY
    assert memory.entries(Tier.SHARED) == ()


def test_two_colluders_get_a_false_fact_past_the_kernel(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0, colluding=True)
    plant(world, plan)
    false = next(p for p in plan.plantings if not p.fact.truth)
    listener = next(n for n in NAMES if n not in false.holders)
    cites = tuple(tell(world.log, h, listener, false.fact.text) for h in false.holders)
    entry = Memory(world.log, admit).write_claim(
        listener, false.fact.text, Kind.TOLD, cites, Tier.SHARED
    )
    assert entry.admission is Admission.FACT


def test_the_planting_replays_and_every_arm_forks_from_it(tmp_path):
    world = fresh(tmp_path, name="base.jsonl")
    announce(world, ROSTER)
    world.runner.run(3)
    snapshot = plant(world, make_plan(generate(1, 0), ROSTER, 1, 0))
    world.runner.run(3)
    result = audit(world.log, tmp_path / "replay.jsonl", 1, BASE, CONFIG)
    assert result.ok

    run = launch(
        snapshot,
        world.log,
        tmp_path / "arms",
        [NO_DEFENSE, KERNEL_ADMISSION],
        lambda: FakeBackend(gossip),
        CONFIG,
    )
    for arm in run.worlds.values():
        assert len([e for e in arm.log if e.kind == "plant"]) == 10
        assert arm.log.head_at(snapshot.events) == snapshot.head


def test_a_plan_is_a_frozen_value():
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    assert isinstance(plan, Plan)
    with pytest.raises(AttributeError):
        plan.colluding = True


def utility_plan(colluding=False, block=0):
    facts = generate(1, block) + utility_facts(1, block)
    return make_plan(facts, ROSTER, 1, block, colluding)


@pytest.mark.parametrize("colluding", [False, True])
def test_a_utility_fact_has_one_holder_from_the_group_its_status_calls_for(colluding):
    for block in range(4):
        plan = utility_plan(colluding, block)
        for p in plan.plantings:
            if p.fact.utility:
                group = ROSTER.elders if p.fact.status is Level.HIGH else ROSTER.others
                assert len(p.holders) == 1 and p.holders[0] in group
            else:
                assert len(p.holders) == (2 if p.fact.truth or colluding else 1)


def test_adding_utility_facts_leaves_the_holders_of_the_ten_unchanged():
    ten = make_plan(generate(1, 0), ROSTER, 1, 0)
    assert utility_plan().plantings[:10] == ten.plantings


def test_the_planting_marker_says_which_facts_are_utility_facts(tmp_path):
    world = fresh(tmp_path)
    plant(world, utility_plan())
    markers = {e.payload["fact"]: e.payload for e in world.log if e.kind == "plant"}
    assert {k for k, m in markers.items() if m["utility"]} == {"u1", "u2"}
    assert len(markers) == 12 and all(len(markers[k]["holders"]) == 1 for k in ("u1", "u2"))


def test_a_utility_fact_is_given_to_its_one_holder_only(tmp_path):
    world = fresh(tmp_path)
    plan = utility_plan()
    plant(world, plan)
    for p in plan.plantings:
        if p.fact.utility:
            seers = [e.writer for e in world.log if e.payload.get("text") == p.fact.observation]
            assert seers == list(p.holders)


def test_the_kernel_hears_a_utility_fact_from_its_single_witness_as_hearsay(tmp_path):
    world = fresh(tmp_path)
    plan = utility_plan()
    plant(world, plan)
    utility = next(p for p in plan.plantings if p.fact.utility)
    listener = next(n for n in NAMES if n not in utility.holders)
    told = tell(world.log, utility.holders[0], listener, utility.fact.text)
    entry = Memory(world.log, admit).write_claim(
        listener, utility.fact.text, Kind.TOLD, (told,), Tier.SHARED
    )
    assert entry.admission is Admission.HEARSAY


def test_the_corroborated_policy_stops_a_lone_witness_from_publishing_a_false_fact(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    plant(world, plan)
    false = next(p for p in plan.plantings if not p.fact.truth)
    (witness,) = false.holders
    seen = next(
        str(e.id)
        for e in world.log
        if e.kind == "saw" and e.writer == witness and e.payload["text"] == false.fact.observation
    )
    kernel = Memory(world.log, admit).write_claim(
        witness, false.fact.text, Kind.SEEN, (seen,), Tier.SHARED
    )
    strict = Memory(world.log, admit_corroborated).write_claim(
        witness, false.fact.text, Kind.SEEN, (seen,), Tier.SHARED
    )
    assert kernel.admission is Admission.FACT and strict.admission is Admission.HEARSAY


def test_a_true_fact_with_two_witnesses_still_reaches_the_wiki_when_one_tells_the_other(tmp_path):
    world = fresh(tmp_path)
    plan = make_plan(generate(1, 0), ROSTER, 1, 0)
    plant(world, plan)
    true = next(p for p in plan.plantings if p.fact.truth)
    first, second = true.holders
    seen = next(
        str(e.id)
        for e in world.log
        if e.kind == "saw" and e.writer == first and e.payload["text"] == true.fact.observation
    )
    told = tell(world.log, second, first, true.fact.text)
    entry = Memory(world.log, admit_corroborated).write_claim(
        first, true.fact.text, Kind.SEEN, (seen, told), Tier.SHARED
    )
    assert entry.admission is Admission.FACT and entry.tier is Tier.SHARED
