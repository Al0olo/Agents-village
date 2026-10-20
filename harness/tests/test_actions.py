import pytest

from agent_village.actions import (
    MAX_NOTES,
    ActionError,
    Forward,
    Note,
    Remember,
    Say,
    Sleep,
    parse,
    parse_notes,
)
from agent_village.admission import Kind
from agent_village.memory import Tier


def test_say():
    assert parse('{"action": "say", "to": "bo", "text": "hello"}') == Say("bo", "hello")


def test_forward_accepts_an_integer_or_a_numeric_string():
    assert parse('{"action": "forward", "to": "bo", "told": 7}') == Forward("bo", "7")
    assert parse('{"action": "forward", "to": "bo", "told": "7"}') == Forward("bo", "7")


def test_remember():
    reply = '{"action": "remember", "text": "x", "kind": "seen", "cites": [3, "4"], "tier": "core"}'
    assert parse(reply) == Remember("x", Kind.SEEN, ("3", "4"), Tier.CORE)


def test_remember_with_no_citations():
    reply = '{"action": "remember", "text": "x", "kind": "told", "cites": [], "tier": "shared"}'
    assert parse(reply) == Remember("x", Kind.TOLD, (), Tier.SHARED)


def test_sleep():
    assert parse('{"action": "sleep", "ticks": 5}') == Sleep(5)


def test_surrounding_prose_and_code_fences_are_tolerated():
    reply = 'Sure, I will rest.\n```json\n{"action": "sleep", "ticks": 2}\n```\nDone.'
    assert parse(reply) == Sleep(2)


def test_braces_in_prose_before_the_action_are_skipped():
    reply = 'Thinking about {this} and {"a": 1} first. {"action": "sleep", "ticks": 3}'
    assert parse(reply) == Sleep(3)


def test_braces_inside_a_string_value_do_not_confuse_the_parser():
    reply = '{"action": "say", "to": "bo", "text": "use {curly} braces } {"}'
    assert parse(reply) == Say("bo", "use {curly} braces } {")


def test_only_the_first_action_is_used():
    reply = '{"action": "sleep", "ticks": 1} {"action": "say", "to": "bo", "text": "hi"}'
    assert parse(reply) == Sleep(1)


def test_extra_keys_are_ignored():
    assert parse('{"action": "sleep", "ticks": 1, "mood": "calm"}') == Sleep(1)


@pytest.mark.parametrize(
    "reply",
    [
        "",
        "I will rest.",
        "[1, 2, 3]",
        '{"ticks": 3}',
        '{"action": 3}',
        '{"action": "dance"}',
        '{"action": "say", "to": "bo"}',
        '{"action": "say", "text": "hi"}',
        '{"action": "say", "to": "", "text": "hi"}',
        '{"action": "say", "to": "bo", "text": ""}',
        '{"action": "say", "to": 5, "text": "hi"}',
        '{"action": "say", "to": "bo", "text": 5}',
        '{"action": "forward", "to": "bo"}',
        '{"action": "forward", "to": "bo", "told": -1}',
        '{"action": "forward", "to": "bo", "told": "abc"}',
        '{"action": "forward", "to": "bo", "told": true}',
        '{"action": "forward", "to": "bo", "told": 1.5}',
        '{"action": "forward", "to": "", "told": 1}',
        '{"action": "sleep"}',
        '{"action": "sleep", "ticks": 0}',
        '{"action": "sleep", "ticks": -3}',
        '{"action": "sleep", "ticks": 2.5}',
        '{"action": "sleep", "ticks": "5"}',
        '{"action": "sleep", "ticks": true}',
        '{"action": "remember", "kind": "seen", "cites": [], "tier": "core"}',
        '{"action": "remember", "text": "", "kind": "seen", "cites": [], "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "dreamt", "cites": [], "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": [], "tier": "recall"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": [], "tier": "vault"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": "1", "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": [-1], "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": ["a"], "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": [true], "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "seen", "tier": "core"}',
        '{"action": "remember", "text": "x", "cites": [], "tier": "core"}',
        '{"action": "remember", "text": "x", "kind": "seen", "cites": []}',
    ],
)
def test_invalid_replies_raise_action_error(reply):
    with pytest.raises(ActionError):
        parse(reply)


def test_action_error_is_a_value_error_with_a_reason():
    with pytest.raises(ValueError, match="no JSON action"):
        parse("nothing here")


def test_a_note_list_parses_text_and_cites():
    notes = parse_notes('{"notes": [{"text": "Hal counted forty hives", "cites": [12, "15"]}]}')
    assert notes == (Note("Hal counted forty hives", ("12", "15")),)


def test_notes_tolerate_prose_and_fences_and_take_the_first_list():
    reply = 'Here you go:\n```json\n{"notes": [{"text": "a", "cites": []}]}\n```\n{"notes": []}'
    assert parse_notes(reply) == (Note("a", ()),)


def test_an_empty_note_list_is_fine():
    assert parse_notes('{"notes": []}') == ()


def test_notes_are_capped_so_a_review_cannot_write_without_bound():
    many = ", ".join(f'{{"text": "n{i}", "cites": []}}' for i in range(MAX_NOTES + 5))
    assert len(parse_notes(f'{{"notes": [{many}]}}')) == MAX_NOTES


@pytest.mark.parametrize(
    "reply",
    [
        "no json here",
        '{"action": "sleep", "ticks": 1}',
        '{"notes": "text"}',
        '{"notes": {"text": "x", "cites": []}}',
        '{"notes": [{"text": "", "cites": []}]}',
        '{"notes": [{"cites": []}]}',
        '{"notes": [{"text": "x", "cites": "12"}]}',
        '{"notes": [{"text": "x", "cites": [-1]}]}',
        '{"notes": ["x"]}',
    ],
)
def test_a_reply_that_is_not_a_valid_note_list_is_an_error(reply):
    with pytest.raises(ActionError):
        parse_notes(reply)
