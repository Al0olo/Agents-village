import pytest

from agent_village.admission import Admission, Kind, admit
from agent_village.eventlog import EventLog
from agent_village.memory import Memory, Tier
from agent_village.messages import Messenger


def setup(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    return log, Messenger(log)


def test_send_logs_the_message_and_the_recipients_told_event(tmp_path):
    log, mail = setup(tmp_path)
    delivery = mail.send("bo", "ada", "the well is dry")
    message, told = log[delivery.message], log[delivery.told]
    assert (message.kind, message.writer) == ("message", "bo")
    assert message.payload == {
        "to": "ada",
        "text": "the well is dry",
        "origins": ["bo"],
        "forward_of": None,
    }
    assert (told.kind, told.writer) == ("told", "ada")
    assert told.payload == {
        "from": "bo",
        "text": "the well is dry",
        "origins": ["bo"],
        "message": delivery.message,
    }


def test_received_lists_only_the_recipients_messages_in_order(tmp_path):
    _, mail = setup(tmp_path)
    mail.send("bo", "ada", "one")
    mail.send("bo", "cy", "other")
    mail.send("cy", "ada", "two")
    got = mail.received("ada")
    assert [(m.sender, m.text) for m in got] == [("bo", "one"), ("cy", "two")]
    assert got[0].origins == frozenset({"bo"})
    assert mail.received("di") == ()


def test_received_after_skips_what_the_citizen_has_seen(tmp_path):
    _, mail = setup(tmp_path)
    mail.send("bo", "ada", "one")
    second = mail.send("bo", "ada", "two")
    first_seen = mail.received("ada")[0].id
    assert [m.text for m in mail.received("ada", after=first_seen)] == ["two"]
    assert mail.received("ada", after=second.told) == ()


def test_forward_keeps_the_text_and_adds_the_forwarder_to_the_origins(tmp_path):
    log, mail = setup(tmp_path)
    first = mail.send("bo", "cy", "the well is dry")
    delivery = mail.forward("cy", "ada", str(first.told))
    told = log[delivery.told]
    assert told.writer == "ada"
    assert told.payload["text"] == "the well is dry"
    assert told.payload["from"] == "cy"
    assert told.payload["origins"] == ["bo", "cy"]
    assert log[delivery.message].payload["forward_of"] == first.told


def test_origins_accumulate_over_many_hops_and_never_shrink(tmp_path):
    _, mail = setup(tmp_path)
    hop = mail.send("bo", "cy", "x")
    for sender, receiver in (("cy", "di"), ("di", "ed")):
        hop = mail.forward(sender, receiver, str(hop.told))
    assert mail.received("ed")[0].origins == frozenset({"bo", "cy", "di"})


@pytest.mark.parametrize(
    "forwarder,told_id",
    [("di", "1"), ("cy", "0"), ("cy", "99"), ("cy", "-1"), ("cy", "abc")],
)
def test_forward_needs_a_told_event_the_forwarder_received(tmp_path, forwarder, told_id):
    log, mail = setup(tmp_path)
    mail.send("bo", "cy", "x")
    size = len(log)
    with pytest.raises((ValueError, KeyError)):
        mail.forward(forwarder, "ada", told_id)
    assert len(log) == size


def test_a_message_cannot_return_to_one_of_its_origins(tmp_path):
    log, mail = setup(tmp_path)
    first = mail.send("bo", "cy", "x")
    size = len(log)
    with pytest.raises(ValueError):
        mail.forward("cy", "bo", str(first.told))
    assert len(log) == size


@pytest.mark.parametrize(
    "sender,recipient,text",
    [("ada", "ada", "x"), ("", "ada", "x"), ("bo", "", "x"), ("bo", "ada", "")],
)
def test_invalid_sends_are_rejected_without_logging(tmp_path, sender, recipient, text):
    log, mail = setup(tmp_path)
    with pytest.raises(ValueError):
        mail.send(sender, recipient, text)
    assert len(log) == 0


def test_two_independent_tellers_let_memory_admit_a_fact(tmp_path):
    log, mail = setup(tmp_path)
    cites = tuple(str(mail.send(who, "ada", "the well is dry").told) for who in ("bo", "cy"))
    memory = Memory(log, admit)
    entry = memory.write_claim("ada", "the well is dry", Kind.TOLD, cites, Tier.SHARED)
    assert entry.admission is Admission.FACT


def test_forwarding_does_not_launder_one_source_into_two(tmp_path):
    log, mail = setup(tmp_path)
    to_cy = mail.send("bo", "cy", "the well is dry")
    direct = mail.send("bo", "ada", "the well is dry")
    relayed = mail.forward("cy", "ada", str(to_cy.told))
    cites = (str(direct.told), str(relayed.told))
    entry = Memory(log, admit).write_claim("ada", "x", Kind.TOLD, cites, Tier.SHARED)
    assert entry.admission is Admission.HEARSAY


def test_a_long_forward_chain_back_to_one_source_stays_hearsay(tmp_path):
    log, mail = setup(tmp_path)
    one = mail.send("bo", "cy", "x")
    two = mail.forward("cy", "di", str(one.told))
    via_di = mail.forward("di", "ada", str(two.told))
    other = mail.send("bo", "ada", "x")
    cites = (str(via_di.told), str(other.told))
    entry = Memory(log, admit).write_claim("ada", "x", Kind.TOLD, cites, Tier.CORE)
    assert entry.admission is Admission.HEARSAY


def test_colluding_senders_count_as_independent_sources(tmp_path):
    log, mail = setup(tmp_path)
    cites = tuple(str(mail.send(who, "ada", "lie").told) for who in ("mal1", "mal2"))
    entry = Memory(log, admit).write_claim("ada", "lie", Kind.TOLD, cites, Tier.CORE)
    assert entry.admission is Admission.FACT
