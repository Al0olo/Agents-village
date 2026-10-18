import random

import pytest
from villages import NAMES, drive, gossip, specs

from agent_village.admission import Admission, Claim, Event, Kind, admit
from agent_village.arms import ARMS, BASE, KERNEL_ADMISSION, NO_DEFENSE, admit_all
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
