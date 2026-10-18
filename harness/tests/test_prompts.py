import pytest

from agent_village.actions import parse
from agent_village.prompts import ACTION_FORMAT, BASELINE, Prompt


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
