"""Property tests: invariants that must hold on many random histories, not on one example.

Each test draws its histories from seeded generators, so a failure names its seed and
reproduces. The oracles are written independently of the code under test.
"""

import itertools
import random

import pytest
from villages import NAMES, drive, gossip, specs

from agent_village.admission import Admission, Claim, Event, Kind, admit, admit_corroborated
from agent_village.arms import BASE, KERNEL_ADMISSION, NO_DEFENSE, admit_all
from agent_village.consolidation import CONSOLIDATION, run_consolidation
from agent_village.eventlog import EventLog
from agent_village.facts import generate, utility_facts
from agent_village.fork import build, fork
from agent_village.launch import RunConfig
from agent_village.messages import Messenger
from agent_village.model import FakeBackend
from agent_village.planting import Roster, announce, make_plan, plant
from agent_village.probes import PROBE_ROUND, questions, run_round
from agent_village.replay import audit

SEEDS = range(25)
CONFIG = RunConfig(tuple(specs()), 3)
CITIZENS = NAMES[:6]


def random_traffic(seed, steps=40):
    """Random sends and forwards, with an oracle of each told event's origins."""
    rng = random.Random(seed)
    import tempfile
    from pathlib import Path

    log = EventLog(Path(tempfile.mkdtemp()) / "m.jsonl")
    mail = Messenger(log)
    held = {name: [] for name in CITIZENS}
    oracle = {}
    texts = {}
    for n in range(steps):
        sender, recipient = rng.sample(CITIZENS, 2)
        if held[sender] and rng.random() < 0.6:
            source = rng.choice(held[sender])
            expected = oracle[source] | {sender}
            try:
                delivery = mail.forward(sender, recipient, str(source))
            except ValueError:
                assert recipient in expected
                continue
            texts[delivery.told] = texts[source]
            oracle[delivery.told] = expected
        else:
            delivery = mail.send(sender, recipient, f"news {n}")
            texts[delivery.told] = f"news {n}"
            oracle[delivery.told] = {sender}
        held[recipient].append(delivery.told)
    return log, oracle, texts, held


@pytest.mark.parametrize("seed", SEEDS)
def test_origins_in_the_log_are_exactly_the_roots_and_forwarders_of_each_chain(seed):
    log, oracle, texts, _ = random_traffic(seed)
    for told, origins in oracle.items():
        event = log[told]
        assert set(event.payload["origins"]) == origins
        assert event.payload["text"] == texts[told]
        assert event.writer not in origins
        assert event.payload["origins"] == sorted(event.payload["origins"])


@pytest.mark.parametrize("seed", SEEDS)
def test_origins_only_grow_along_a_forward(seed):
    log, _, _, _ = random_traffic(seed)
    for event in log:
        if event.kind == "message" and event.payload["forward_of"] is not None:
            source = log[event.payload["forward_of"]]
            assert set(source.payload["origins"]) < set(event.payload["origins"])
            assert event.writer in event.payload["origins"]


def events_of(log, citizen):
    return {
        str(e.id): Event(
            str(e.id),
            e.writer,
            Kind.TOLD if e.kind in ("told", "heard") else Kind.SEEN,
            frozenset(e.payload.get("origins", ())),
        )
        for e in log
        if e.kind in ("told", "heard", "saw") and e.writer == citizen
    }


def oracle_admits(claim, evidence):
    mine = [
        evidence[c] for c in claim.cites if c in evidence and evidence[c].writer == claim.writer
    ]
    if any(e.kind is Kind.SEEN for e in mine):
        return True
    told = [e for e in mine if e.kind is Kind.TOLD and claim.writer not in e.origins]
    return any(a.origins.isdisjoint(b.origins) for a, b in itertools.combinations(told, 2))


@pytest.mark.parametrize("seed", SEEDS)
def test_the_kernel_agrees_with_an_independent_oracle_on_random_claims(seed):
    log, _, _, _ = random_traffic(seed)
    rng = random.Random(seed)
    for name in CITIZENS:
        log.append("saw", name, {"text": f"{name} saw something"})
        for _ in range(2):
            origins = sorted(rng.sample(CITIZENS, rng.randint(1, 3)))
            log.append("told", name, {"from": "x", "text": "t", "origins": origins})
    for name in CITIZENS:
        evidence = events_of(log, name)
        everyone = {str(e.id): Event(str(e.id), e.writer, Kind.SEEN) for e in log}
        pool = list(evidence) + rng.sample(list(everyone), 5)
        for _ in range(30):
            cites = tuple(rng.sample(pool, rng.randint(0, 4)))
            claim = Claim("x", name, cites, shared=rng.random() < 0.5)
            fact = admit(claim, {**everyone, **evidence}) is Admission.FACT
            assert fact == oracle_admits(claim, {**everyone, **evidence}), (name, cites)
            assert admit_all(claim, evidence) is Admission.FACT
            if admit_corroborated(claim, {**everyone, **evidence}) is Admission.FACT:
                assert fact


@pytest.mark.parametrize("seed", SEEDS)
def test_citing_more_events_never_turns_a_fact_into_hearsay(seed):
    log, _, _, _ = random_traffic(seed)
    rng = random.Random(seed + 1000)
    for name in CITIZENS:
        evidence = events_of(log, name)
        ids = list(evidence)
        for _ in range(20):
            cites = rng.sample(ids, min(len(ids), rng.randint(0, 3)))
            more = cites + rng.sample(ids, min(len(ids), 2))
            before = admit(Claim("x", name, tuple(cites)), evidence)
            after = admit(Claim("x", name, tuple(dict.fromkeys(more))), evidence)
            assert not (before is Admission.FACT and after is Admission.HEARSAY)


@pytest.mark.parametrize("seed", SEEDS)
def test_events_that_share_a_root_never_corroborate_each_other(seed):
    log, oracle, _, held = random_traffic(seed, steps=60)
    for name, told in held.items():
        evidence = events_of(log, name)
        for a, b in itertools.combinations(told, 2):
            if oracle[a] & oracle[b]:
                claim = Claim("x", name, (str(a), str(b)))
                assert admit(claim, evidence) is Admission.HEARSAY


@pytest.mark.parametrize("seed", SEEDS)
def test_a_claim_citing_only_other_citizens_events_is_always_hearsay(seed):
    log, _, _, _ = random_traffic(seed)
    for name in CITIZENS:
        mine = events_of(log, name)
        theirs = {k: v for k, v in events_of(log, CITIZENS[0]).items() if v.writer != name}
        claim = Claim("x", name, tuple(theirs))
        assert admit(claim, {**mine, **theirs}) is Admission.HEARSAY


def village(tmp_path, seed, ticks, name="base.jsonl", policy=BASE.policy):
    world = build(
        EventLog(tmp_path / name),
        random.Random(seed),
        FakeBackend(gossip),
        policy,
        BASE.prompt,
        specs(),
        3,
    )
    drive(world, ticks)
    return world


@pytest.mark.parametrize("seed", range(10))
def test_a_fork_continues_exactly_like_the_base_whatever_the_history(tmp_path, seed):
    rng = random.Random(seed)
    before, after = rng.randint(0, 12), rng.randint(1, 10)
    base = village(tmp_path, seed, before)
    snapshot = base.snapshot()
    branch = fork(
        snapshot,
        base.log,
        tmp_path / "fork.jsonl",
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        specs(),
        3,
    )
    assert branch.state() == base.state()
    drive(base, after)
    drive(branch, after)
    assert (tmp_path / "fork.jsonl").read_bytes() == (tmp_path / "base.jsonl").read_bytes()
    assert branch.log.head == base.log.head


@pytest.mark.parametrize("seed", range(10))
def test_arms_share_the_prefix_and_what_they_wrote_before_the_fork_is_not_reclassified(
    tmp_path, seed
):
    base = village(tmp_path, seed, random.Random(seed).randint(3, 12))
    snapshot = base.snapshot()
    arms = {}
    for arm in (NO_DEFENSE, KERNEL_ADMISSION):
        arms[arm.name] = fork(
            snapshot,
            base.log,
            tmp_path / f"{arm.name}.jsonl",
            FakeBackend(gossip),
            arm.policy,
            arm.prompt,
            specs(),
            3,
        )
        drive(arms[arm.name], 6)
    prefix = [e for e in base.log]
    for world in arms.values():
        assert [world.log[i] for i in range(snapshot.events)] == prefix[: snapshot.events]
    for index in range(snapshot.events):
        assert arms["A"].log[index] == arms["D"].log[index]


def full_village(tmp_path, seed):
    """A village with rumors, a probe round and two reviews, so replay meets every driver action."""
    rng = random.Random(seed)
    roster = Roster(NAMES, ("ada", "bo"))
    facts = generate(1, seed) + utility_facts(1, seed)

    def backend(request):
        if "review your day" in request.messages[0].content:
            return '{"notes": [{"text": "kept", "cites": []}]}'
        return gossip(request)

    world = build(
        EventLog(tmp_path / "full.jsonl"),
        random.Random(seed),
        FakeBackend(backend),
        BASE.policy,
        BASE.prompt,
        specs(),
        3,
    )
    announce(world, roster)
    world.runner.run(rng.randint(1, 3))
    plant(world, make_plan(facts, roster, 1, seed, colluding=seed % 2 == 0, rumors=True))
    world.runner.run(rng.randint(2, 4))
    run_round(world, questions(facts, awareness=False))
    run_consolidation(world, BASE_REVIEW)
    world.runner.run(rng.randint(1, 3))
    run_round(world, questions(facts))
    return world


BASE_REVIEW = NO_DEFENSE.review


@pytest.mark.parametrize("seed", range(10))
def test_a_village_with_every_kind_of_driver_action_replays_to_the_same_bytes(tmp_path, seed):
    world = full_village(tmp_path, seed)
    kinds = {e.kind for e in world.log}
    assert {"heard", "plant", PROBE_ROUND, CONSOLIDATION, "claim"} <= kinds
    result = audit(world.log, tmp_path / "replay.jsonl", seed, BASE, CONFIG)
    assert result.ok and result.events == len(world.log)
    assert (tmp_path / "replay.jsonl").read_bytes() == (tmp_path / "full.jsonl").read_bytes()


DERIVED = ("turn_end", "claim", "message", "told", "probe", "review", "woke", "slept", "step")


@pytest.mark.parametrize("seed", range(10))
def test_tampering_with_any_derived_event_is_reported_at_that_event(tmp_path, seed):
    world = full_village(tmp_path, seed)
    rng = random.Random(seed)
    candidates = [i for i, e in enumerate(world.log) if e.kind in DERIVED]
    for index in rng.sample(candidates, 6):
        edited = EventLog(tmp_path / f"edited-{seed}-{index}.jsonl")
        for i, event in enumerate(world.log):
            payload = dict(event.payload)
            if i == index:
                payload["tampered"] = True
            edited.append(event.kind, event.writer, payload)
        result = audit(edited, tmp_path / f"r-{seed}-{index}.jsonl", seed, BASE, CONFIG)
        assert result.divergence is not None and result.divergence.index == index, (
            seed,
            index,
            world.log[index].kind,
        )
