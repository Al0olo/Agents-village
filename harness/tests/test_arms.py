import random

import pytest
from villages import NAMES, drive, gossip, specs

from agent_village.admission import Admission, Claim, Event, Kind, admit
from agent_village.arms import (
    ARMS,
    BASE,
    KERNEL_ADMISSION,
    NO_DEFENSE,
    RandomBlock,
    admit_all,
    matched_rate,
    random_block_arm,
)
from agent_village.eventlog import EventLog
from agent_village.fork import build, fork
from agent_village.memory import Tier
from agent_village.model import FakeBackend


@pytest.fixture(scope="module")
def arms_run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("arms")
    log = EventLog(tmp / "base.jsonl")
    base = build(log, random.Random(5), FakeBackend(gossip), BASE.policy, BASE.prompt, specs(), 3)
    drive(base, 24)
    snap = base.snapshot()
    worlds = {}
    for arm in (NO_DEFENSE, KERNEL_ADMISSION):
        worlds[arm.name] = fork(
            snap,
            base.log,
            tmp / f"{arm.name}.jsonl",
            FakeBackend(gossip),
            arm.policy,
            arm.prompt,
            specs(),
            3,
        )
        drive(worlds[arm.name], 48)
    return snap, worlds


def claims(world, after=0):
    return [e for e in world.log if e.kind == "claim" and e.id >= after]


def oracle(log, claim):
    """Recompute a logged admission decision from the log alone."""
    cited = [
        log[int(c)]
        for c in claim.payload["cites"]
        if c.isdigit() and int(c) < claim.id and log[int(c)].writer == claim.writer
    ]
    if any(e.kind in ("saw", "did") for e in cited):
        return "fact"
    tellers = [
        set(e.payload["origins"])
        for e in cited
        if e.kind == "told" and e.payload["origins"] and e.writer not in e.payload["origins"]
    ]
    independent = any(a.isdisjoint(b) for i, a in enumerate(tellers) for b in tellers[i + 1 :])
    return "fact" if independent else "hearsay"


def test_the_registry_holds_the_arms_by_their_names():
    assert set(ARMS) == {"A", "D"}
    assert all(arm.name == name for name, arm in ARMS.items())


def test_arms_differ_only_in_the_memory_policy():
    assert NO_DEFENSE.prompt is KERNEL_ADMISSION.prompt
    assert NO_DEFENSE.policy is admit_all
    assert KERNEL_ADMISSION.policy is admit


@pytest.mark.parametrize(
    "claim,events",
    [
        (Claim("x", "ada", ()), {}),
        (Claim("x", "ada", ("nope",)), {}),
        (Claim("x", "ada", ("e1",)), {"e1": Event("e1", "bo", Kind.SEEN)}),
        (Claim("x", "ada", ("e1",)), {"e1": Event("e1", "ada", Kind.TOLD, frozenset({"bo"}))}),
    ],
)
def test_no_defense_admits_everything_the_kernel_would_refuse(claim, events):
    assert NO_DEFENSE.policy(claim, events) is Admission.FACT
    assert KERNEL_ADMISSION.policy(claim, events) is Admission.HEARSAY


def test_the_scenario_exercises_forwards_and_both_outcomes(arms_run):
    _, worlds = arms_run
    kernel = worlds["D"]
    forwards = [
        e for e in kernel.log if e.kind == "message" and e.payload["forward_of"] is not None
    ]
    outcomes = {e.payload["admission"] for e in claims(kernel)}
    multi = [
        e for e in claims(kernel) if len(e.payload["cites"]) >= 2 and e.payload["kind"] == "told"
    ]
    assert forwards and multi
    assert outcomes == {"fact", "hearsay"}


def test_arms_start_identical_and_diverge_only_after_the_fork(arms_run):
    snap, worlds = arms_run
    a, d = worlds["A"].log, worlds["D"].log
    first = next(i for i, (x, y) in enumerate(zip(a, d)) if x != y)
    assert first >= snap.events
    assert a.head_at(snap.events) == d.head_at(snap.events) == snap.head


def test_kernel_admission_matches_an_independent_recomputation(arms_run):
    snap, worlds = arms_run
    kernel = worlds["D"]
    after = claims(kernel, snap.events)
    assert after
    for claim in after:
        assert claim.payload["admission"] == oracle(kernel.log, claim), claim.id


def test_no_hearsay_written_under_the_kernel_reaches_core_or_shared(arms_run):
    snap, worlds = arms_run
    kernel = worlds["D"]
    stored = list(kernel.memory.entries(Tier.SHARED))
    stored += [e for n in NAMES for e in kernel.memory.entries(Tier.CORE, n)]
    written = [e for e in stored if e.id >= snap.events]
    assert written
    for entry in written:
        assert entry.admission is Admission.FACT
        assert oracle(kernel.log, kernel.log[entry.id]) == "fact"


def test_hearsay_is_kept_in_recall_not_discarded(arms_run):
    snap, worlds = arms_run
    kernel = worlds["D"]
    hearsay = [e for e in claims(kernel, snap.events) if e.payload["admission"] == "hearsay"]
    recalled = [
        e for n in NAMES for e in kernel.memory.entries(Tier.RECALL, n) if e.id >= snap.events
    ]
    assert hearsay and len(recalled) == len(hearsay)


def test_the_base_village_runs_without_defense():
    assert BASE is NO_DEFENSE
    assert BASE.policy is admit_all


def test_everything_the_base_stored_is_fact_and_some_of_it_has_no_backing(arms_run):
    snap, worlds = arms_run
    before = [e for e in claims(worlds["D"]) if e.id < snap.events]
    assert before
    assert {e.payload["admission"] for e in before} == {"fact"}
    assert any(oracle(worlds["D"].log, e) == "hearsay" for e in before)


def test_the_kernel_does_not_reclassify_what_the_base_stored(arms_run):
    snap, worlds = arms_run
    kernel = worlds["D"]
    unbacked = [
        e for e in claims(kernel) if e.id < snap.events and oracle(kernel.log, e) == "hearsay"
    ]
    assert unbacked
    for claim in unbacked:
        tier = Tier(claim.payload["stored"])
        held = kernel.memory.entries(tier, claim.writer)
        assert any(entry.id == claim.id for entry in held)


def test_no_defense_stores_every_claim_as_fact_after_the_fork(arms_run):
    snap, worlds = arms_run
    none = worlds["A"]
    after = claims(none, snap.events)
    assert after
    assert {e.payload["admission"] for e in after} == {"fact"}
    assert all(e.payload["stored"] == e.payload["requested"] for e in after)


def test_the_kernel_adds_less_to_shared_memory_than_no_defense(arms_run):
    snap, worlds = arms_run
    added = {
        name: len([e for e in w.memory.entries(Tier.SHARED) if e.id >= snap.events])
        for name, w in worlds.items()
    }
    assert added["D"] < added["A"]


def test_origins_in_the_log_follow_the_forward_chain_exactly(arms_run):
    _, worlds = arms_run
    for world in worlds.values():
        told_origins = {}
        for event in world.log:
            if event.kind == "message":
                parent = event.payload["forward_of"]
                if parent is None:
                    expected = {event.writer}
                else:
                    forwarded = world.log[parent]
                    assert forwarded.kind == "told" and forwarded.writer == event.writer
                    expected = told_origins[parent] | {event.writer}
                assert set(event.payload["origins"]) == expected
                delivered = world.log[event.id + 1]
                assert delivered.kind == "told"
                assert delivered.payload["origins"] == event.payload["origins"]
            elif event.kind == "told":
                told_origins[event.id] = set(event.payload["origins"])
                assert event.writer not in told_origins[event.id]


def many_claims(n=2000, cites=()):
    return [Claim(f"claim {i}", NAMES[i % len(NAMES)], cites) for i in range(n)]


def blocked_share(policy, claims, evidence=None):
    blocked = sum(policy(c, evidence or {}) is Admission.HEARSAY for c in claims)
    return blocked / len(claims)


@pytest.mark.parametrize("rate", [-0.1, 1.1, float("nan")])
def test_a_block_rate_must_be_a_share(rate):
    with pytest.raises(ValueError):
        RandomBlock(rate, "s")


@pytest.mark.parametrize("rate", [0.0, 1.0])
def test_a_random_block_at_the_extremes_admits_all_or_blocks_all(rate):
    outcomes = {RandomBlock(rate, "s")(c, {}) for c in many_claims(200)}
    assert outcomes == {Admission.HEARSAY if rate else Admission.FACT}


@pytest.mark.parametrize("rate", [0.1, 0.3, 0.5, 0.9])
def test_a_random_block_blocks_about_its_rate_of_distinct_claims(rate):
    assert abs(blocked_share(RandomBlock(rate, "s"), many_claims()) - rate) < 0.03


def test_the_decision_is_fixed_by_the_claim_whatever_the_evidence():
    policy = RandomBlock(0.5, "s")
    backed = {"e1": Event("e1", "ada", Kind.SEEN)}
    for claim in many_claims(200, cites=("e1",)):
        assert policy(claim, backed) is policy(claim, {}) is policy(claim, backed)


def test_blocking_ignores_provenance_so_backed_claims_are_blocked_as_often_as_unbacked():
    policy = RandomBlock(0.5, "s")
    backed = {"e1": Event("e1", "ada", Kind.SEEN)}
    claims = [Claim(f"c{i}", "ada", ("e1",)) for i in range(2000)]
    assert abs(blocked_share(policy, claims, backed) - 0.5) < 0.03
    assert all(admit(c, backed) is Admission.FACT for c in claims)


@pytest.mark.parametrize(
    "other",
    [
        lambda c: Claim(c.text + "!", c.writer, c.cites),
        lambda c: Claim(c.text, c.writer + "x", c.cites),
        lambda c: Claim(c.text, c.writer, c.cites + ("e9",)),
    ],
)
def test_every_part_of_the_claim_keys_the_decision(other):
    policy = RandomBlock(0.5, "s")
    claims = many_claims(400)
    assert any(policy(c, {}) is not policy(other(c), {}) for c in claims)


def test_the_salt_keys_the_decision():
    a, b = RandomBlock(0.5, "one"), RandomBlock(0.5, "two")
    assert any(a(c, {}) is not b(c, {}) for c in many_claims(400))
    assert RandomBlock(0.5, "one") == a and hash(a) == hash(RandomBlock(0.5, "one"))


def test_the_random_block_arm_differs_from_no_defense_only_in_its_policy():
    arm = random_block_arm(0.4, "pilot-1")
    assert arm.name == "E" and arm.prompt is NO_DEFENSE.prompt
    assert arm.policy == RandomBlock(0.4, "pilot-1")
    assert arm.settings == {"rate": 0.4, "salt": "pilot-1"}
    assert NO_DEFENSE.settings == KERNEL_ADMISSION.settings == {}
    assert "E" not in ARMS


def test_the_matched_rate_is_the_share_of_claims_the_kernel_stored_as_hearsay(arms_run):
    snap, worlds = arms_run
    after = claims(worlds["D"], snap.events)
    hearsay = [e for e in after if e.payload["admission"] == "hearsay"]
    assert 0 < len(hearsay) < len(after)
    assert matched_rate(worlds["D"].log, snap.events) == len(hearsay) / len(after)
    assert matched_rate(worlds["A"].log, snap.events) == 0.0


def test_claims_before_the_start_do_not_count_toward_the_matched_rate(arms_run):
    snap, worlds = arms_run
    everything = matched_rate(worlds["D"].log, 0)
    assert everything != matched_rate(worlds["D"].log, snap.events)


def test_the_claim_at_the_start_position_counts(tmp_path):
    log = EventLog(tmp_path / "c.jsonl")
    for admission in ("hearsay", "fact", "fact", "fact"):
        log.append("claim", "ada", {"admission": admission})
    assert matched_rate(log, 0) == 0.25
    assert matched_rate(log, 1) == 0.0
    assert matched_rate(log, 3) == 0.0


def test_a_rate_cannot_be_matched_from_a_log_without_claims(tmp_path):
    with pytest.raises(ValueError):
        matched_rate(EventLog(tmp_path / "empty.jsonl"), 0)


def test_in_a_village_the_random_block_stores_backed_and_unbacked_claims_alike(arms_run, tmp_path):
    snap, worlds = arms_run
    arm = random_block_arm(matched_rate(worlds["D"].log, snap.events), "s")
    world = fork(
        snap,
        worlds["D"].log,
        tmp_path / "E.jsonl",
        FakeBackend(gossip),
        arm.policy,
        arm.prompt,
        specs(),
        3,
    )
    drive(world, 48)
    after = claims(world, snap.events)
    backed = [e for e in after if oracle(world.log, e) == "fact"]
    assert backed and any(e.payload["admission"] == "hearsay" for e in backed)
    assert any(e.payload["admission"] == "fact" for e in after if oracle(world.log, e) == "hearsay")
