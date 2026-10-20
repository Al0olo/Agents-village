import random

import pytest
from villages import NAMES, SAW_LINE, TOLD_LINE, gossip

from agent_village.arms import BASE, KERNEL_ADMISSION, NO_DEFENSE, STANCE_PRESERVING, Arm
from agent_village.consolidation import CONSOLIDATION, run_consolidation
from agent_village.eventlog import EventLog
from agent_village.fork import ENVIRONMENT, build
from agent_village.launch import RunConfig
from agent_village.model import FakeBackend
from agent_village.prompts import REVIEW_DEFAULT, REVIEW_HEDGE_PRESERVING, Prompt
from agent_village.replay import audit, branch
from agent_village.runner import Spec

SPECS = [Spec(n, "fake/model") for n in NAMES]
CONFIG = RunConfig(tuple(SPECS), 3)


def reviewing(request):
    """Gossip in the turns; in a review, one note citing the first thing seen or told."""
    if "review your day" not in request.messages[0].content:
        return gossip(request)
    user = request.messages[1].content
    seen, told = SAW_LINE.findall(user), TOLD_LINE.findall(user)
    if seen:
        return f'{{"notes": [{{"text": "I saw it", "cites": [{seen[0]}]}}]}}'
    if told:
        return f'{{"notes": [{{"text": "I was told it", "cites": [{told[0][0]}]}}]}}'
    return '{"notes": []}'


def make(tmp_path, name="v.jsonl", policy=BASE.policy):
    return build(
        EventLog(tmp_path / name),
        random.Random(1),
        FakeBackend(reviewing),
        policy,
        BASE.prompt,
        SPECS,
        3,
    )


def lived(tmp_path, ticks=6, **over):
    world = make(tmp_path, **over)
    for tick in range(ticks):
        if tick % 2 == 0:
            world.log.append("saw", NAMES[tick % 8], {"text": f"observation {tick}"})
        world.runner.tick()
    return world


def test_a_consolidation_is_a_marker_then_one_review_per_citizen_in_order(tmp_path):
    world = lived(tmp_path)
    start = len(world.log)
    run_consolidation(world, REVIEW_DEFAULT)
    events = [world.log[i] for i in range(start, len(world.log))]
    marker = events[0]
    assert (marker.kind, marker.writer) == (CONSOLIDATION, ENVIRONMENT)
    assert marker.payload == {
        "prompt_version": REVIEW_DEFAULT.version,
        "prompt_hash": REVIEW_DEFAULT.hash,
    }
    assert [e.writer for e in events if e.kind == "review"] == list(NAMES)
    assert [e.writer for e in events if e.kind == "model_call"] == list(NAMES)


def test_a_consolidation_needs_a_village_between_ticks(tmp_path):
    world = lived(tmp_path, ticks=2)
    world.village.step()
    before = len(world.log)
    with pytest.raises(ValueError):
        run_consolidation(world, REVIEW_DEFAULT)
    assert len(world.log) == before


def test_the_consolidation_prompt_reaches_the_model(tmp_path):
    seen = []

    class Spy:
        def complete(self, request):
            seen.append(request.messages[0].content)
            return FakeBackend(reviewing).complete(request)

    world = build(
        EventLog(tmp_path / "v.jsonl"),
        random.Random(1),
        Spy(),
        BASE.policy,
        BASE.prompt,
        SPECS,
        3,
    )
    world.runner.run(2)
    seen.clear()
    run_consolidation(world, REVIEW_HEDGE_PRESERVING)
    assert len(seen) == len(NAMES)
    assert all(REVIEW_HEDGE_PRESERVING.system in s for s in seen)


def test_an_audit_replays_a_consolidation_and_a_branch_reruns_it(tmp_path):
    world = lived(tmp_path, name="base.jsonl")
    run_consolidation(world, REVIEW_DEFAULT)
    world.runner.run(3)
    run_consolidation(world, REVIEW_DEFAULT)
    assert any(e.kind == "claim" for e in world.log if e.kind != "plant")
    result = audit(world.log, tmp_path / "replay.jsonl", 1, NO_DEFENSE, CONFIG)
    assert result.ok and result.events == len(world.log)

    cut = [i for i, e in enumerate(world.log) if e.kind == CONSOLIDATION][1]
    b = branch(world.log, cut, tmp_path / "branch.jsonl", 1, NO_DEFENSE, NO_DEFENSE, CONFIG)
    b.run()
    assert b.world.log.head == world.log.head
    assert b.backend.fresh_requests == []


def test_auditing_a_consolidation_under_another_review_prompt_diverges_there(tmp_path):
    world = lived(tmp_path, name="base.jsonl")
    start = len(world.log)
    run_consolidation(world, REVIEW_DEFAULT)
    result = audit(world.log, tmp_path / "r.jsonl", 1, STANCE_PRESERVING, CONFIG)
    assert result.divergence is not None and result.divergence.index == start
    assert "review" in result.divergence.reason


def test_a_branch_reviews_with_the_new_arms_prompt(tmp_path):
    world = lived(tmp_path, name="base.jsonl")
    cut = len(world.log)
    run_consolidation(world, REVIEW_DEFAULT)
    other = Arm("A", NO_DEFENSE.policy, NO_DEFENSE.prompt, review=Prompt("review-x", "Be brief."))
    b = branch(world.log, cut, tmp_path / "b.jsonl", 1, NO_DEFENSE, other, CONFIG, FakeBackend())
    b.run()
    marker = next(e for e in b.world.log if e.kind == CONSOLIDATION)
    assert marker.payload["prompt_version"] == "review-x"
    assert len(b.backend.fresh_requests) == len(NAMES)


def test_the_kernel_stores_a_review_note_that_cites_only_what_was_told_as_hearsay(tmp_path):
    world = lived(tmp_path, ticks=8, policy=KERNEL_ADMISSION.policy)
    run_consolidation(world, REVIEW_DEFAULT)
    notes = [e for e in world.log if e.kind == "claim" and e.payload["text"] == "I was told it"]
    assert notes
    assert {e.payload["stored"] for e in notes} == {"recall"}
