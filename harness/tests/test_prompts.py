import re

import pytest

from agent_village.actions import parse
from agent_village.prompts import ACTION_FORMAT, ANCHOR_SCRUTINY, BASELINE, CALIBRATED, Prompt


def test_hash_is_stable_and_covers_version_and_text():
    assert Prompt("v1", "text").hash == Prompt("v1", "text").hash
    assert Prompt("v1", "text").hash != Prompt("v2", "text").hash
    assert Prompt("v1", "text").hash != Prompt("v1", "text!").hash


def test_baseline_is_versioned():
    assert BASELINE.version == "baseline-1"
    assert ACTION_FORMAT in BASELINE.system


def test_every_example_in_the_action_format_parses():
    examples = [line for line in ACTION_FORMAT.splitlines() if line.startswith("{")]
    assert len(examples) == 4
    for line in examples:
        filled = (
            line.replace('"<citizen>"', '"bo"')
            .replace('"<message>"', '"hi"')
            .replace('"<what to keep>"', '"x"')
            .replace("<number of a message you were told>", "3")
            .replace('"seen" | "did" | "told"', '"seen"')
            .replace('"core" | "shared"', '"core"')
            .replace("[<numbers of the events behind it>]", "[3]")
            .replace("<how many ticks to sleep>", "4")
        )
        parse(filled)


@pytest.mark.parametrize(
    "word",
    [
        "hearsay",
        "admission",
        "provenance",
        "kernel",
        "experiment",
        "false",
        "defense",
        "origin",
        "verify",
    ],
)
def test_baseline_does_not_leak_the_hypothesis(word):
    assert word not in BASELINE.system.lower()


def test_the_baseline_text_is_pinned():
    assert BASELINE.hash == "6247155c661ce8e0d1f5d39119352fc516cfb3d71741a011d2500fd8663964a7"


def test_the_defense_prompts_are_pinned():
    assert {p.version: p.hash for p in ANCHOR_SCRUTINY} == {
        "anchor-scrutiny-1a": "7b6da192fb01081dff36316ac75abef14475f9a455beaf49d4fc47f90bf434af",
        "anchor-scrutiny-1b": "888b31bd8e14782efd9a7985ebb9cd91407d4c7b705dd7582be3d5348cfa959b",
        "anchor-scrutiny-1c": "4889102cbfdc4ffc7dab8e4405878a5ed9e9405e794c0ac1b98a90f313570578",
    }


def test_there_is_a_primary_prompt_and_two_paraphrases_with_their_own_versions():
    assert [p.version for p in ANCHOR_SCRUTINY] == [
        "anchor-scrutiny-1a",
        "anchor-scrutiny-1b",
        "anchor-scrutiny-1c",
    ]
    assert len({p.hash for p in ANCHOR_SCRUTINY}) == 3


def split(prompt):
    head, sep, tail = prompt.system.partition("\n\n" + ACTION_FORMAT)
    assert sep and not tail
    return head


@pytest.mark.parametrize("prompt", ANCHOR_SCRUTINY, ids=lambda p: p.version)
def test_a_defense_prompt_is_the_baseline_world_with_one_inserted_passage(prompt):
    world = BASELINE.system.partition("\n\n" + ACTION_FORMAT)[0]
    head = split(prompt)
    assert head.startswith(world + "\n\n")
    passage = head[len(world) + 2 :]
    assert passage.count("\n\n") == 1 and 600 < len(passage) < 1400


MOVES = {
    "own experience first": r"\b(saw|seen|senses|eyes)\b",
    "what others say is not proof": r"(say-so|not evidence|not a fact|report from them)",
    "change a view only for a reason": r"reason",
    "several citizens can be one source": r"(one source|single source|one person|one source)",
    "uniform accounts deserve doubt": r"(smoothly|uniform|too neatly)",
    "say whether it was seen or heard before the wiki": r"wiki",
}


@pytest.mark.parametrize("prompt", ANCHOR_SCRUTINY, ids=lambda p: p.version)
@pytest.mark.parametrize("move", MOVES)
def test_every_wording_makes_each_move_of_anchoring_and_scrutiny(prompt, move):
    assert re.search(MOVES[move], prompt.system.lower())


def test_the_paraphrases_say_the_same_things_in_different_words():
    passages = [split(p).partition("\n\n")[2] for p in ANCHOR_SCRUTINY]
    assert len(set(passages)) == 3
    lengths = [len(x) for x in passages]
    assert max(lengths) / min(lengths) < 1.25
    first, second, third = (set(re.findall(r"[a-z]+", x.lower())) for x in passages)
    assert len(first & second) / len(first | second) < 0.6
    assert len(first & third) / len(first | third) < 0.6


@pytest.mark.parametrize("prompt", ANCHOR_SCRUTINY, ids=lambda p: p.version)
@pytest.mark.parametrize(
    "word",
    [
        "hearsay",
        "admission",
        "provenance",
        "kernel",
        "experiment",
        "study",
        "simulat",
        "false",
        "defense",
        "origin",
        "verify",
        "planted",
        "rumour",
        "test",
    ],
)
def test_a_defense_prompt_does_not_leak_the_hypothesis(prompt, word):
    assert word not in prompt.system.lower()


@pytest.mark.parametrize("prompt", ANCHOR_SCRUTINY, ids=lambda p: p.version)
def test_a_defense_prompt_names_no_arm_policy_or_tier_rule(prompt):
    text = prompt.system.lower()
    for phrase in ("two citizens", "at least two", "disjoint", "corroborat"):
        assert phrase not in text


def test_the_calibrated_prompt_is_versioned_and_pinned():
    assert CALIBRATED.version == "anchor-calibrated-1"
    assert CALIBRATED.hash == "e3a00e3a1ae8ff04fb0e038255736b1c02810a38ed3ae98a27f824d014815326"
    assert CALIBRATED.hash not in {p.hash for p in ANCHOR_SCRUTINY}


def test_the_calibrated_prompt_is_the_baseline_world_with_one_inserted_passage():
    world = BASELINE.system.partition("\n\n" + ACTION_FORMAT)[0]
    head, sep, tail = CALIBRATED.system.partition("\n\n" + ACTION_FORMAT)
    assert sep and not tail and head.startswith(world + "\n\n")
    passage = head[len(world) + 2 :]
    assert passage.count("\n\n") == 1 and 600 < len(passage) < 1400


CALIBRATED_MOVES = {
    "own experience first": r"\bsaw\b",
    "pass on what others said with who said it": r"who said it",
    "agreeing independent accounts count for more": r"independent accounts",
    "several citizens can be one source": r"one source",
    "do not dismiss what you did not see": r"dismiss",
    "say how you know before the wiki": r"wiki",
    "do not abdicate": r"only when you have nothing",
}


@pytest.mark.parametrize("move", CALIBRATED_MOVES)
def test_the_calibrated_prompt_makes_each_move(move):
    assert re.search(CALIBRATED_MOVES[move], CALIBRATED.system.lower())


@pytest.mark.parametrize(
    "word",
    ["hearsay", "admission", "provenance", "kernel", "experiment", "study", "simulat", "false"]
    + ["defense", "origin", "verify", "planted", "rumour", "test", "skeptic", "distrust"],
)
def test_the_calibrated_prompt_does_not_leak_the_hypothesis(word):
    assert word not in CALIBRATED.system.lower()
