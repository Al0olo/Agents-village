import json

import pytest

from agent_village.eventlog import GENESIS, EventLog, LogCorruptError


def fill(log):
    log.append("saw", "ada", {"what": "well", "dry": True})
    log.append("told", "bo", {"to": "ada", "text": "the well is dry"})
    log.append("did", "ada", {"act": "fetch water"})


def test_empty_log_head_is_genesis(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    assert len(log) == 0
    assert log.head == GENESIS


def test_ids_are_sequential_and_chain_links(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    fill(log)
    events = list(log)
    assert [e.id for e in events] == [0, 1, 2]
    assert events[0].prev == GENESIS
    assert events[1].prev == events[0].hash
    assert events[2].prev == events[1].hash
    assert log.head == events[2].hash


def test_reopen_reproduces_events_and_continues_chain(tmp_path):
    path = tmp_path / "v.jsonl"
    log = EventLog(path)
    fill(log)
    before = list(log)

    reopened = EventLog(path)
    assert list(reopened) == before
    nxt = reopened.append("did", "bo", {"act": "rest"})
    assert nxt.id == 3
    assert nxt.prev == before[-1].hash


def test_payload_is_normalised_so_live_equals_loaded(tmp_path):
    path = tmp_path / "v.jsonl"
    log = EventLog(path)
    event = log.append("saw", "ada", {"seen": ("a", "b")})
    assert event.payload == {"seen": ["a", "b"]}
    assert list(EventLog(path)) == [event]


def test_hash_ignores_payload_key_order(tmp_path):
    a = EventLog(tmp_path / "a.jsonl").append("saw", "ada", {"x": 1, "y": 2})
    b = EventLog(tmp_path / "b.jsonl").append("saw", "ada", {"y": 2, "x": 1})
    assert a.hash == b.hash


def test_hash_vector_is_pinned(tmp_path):
    event = EventLog(tmp_path / "v.jsonl").append("saw", "ada", {"what": "well"})
    assert event.hash == "9a4a175c54059b8f226e5577429bed733ccd97f1fe3a5b5c2122d3a2912c4022"


def test_file_only_grows_by_appending(tmp_path):
    path = tmp_path / "v.jsonl"
    log = EventLog(path)
    log.append("saw", "ada", {})
    first = path.read_bytes()
    log.append("did", "ada", {})
    assert path.read_bytes().startswith(first)
    assert len(path.read_text().splitlines()) == 2


def test_edited_payload_is_detected(tmp_path):
    path = tmp_path / "v.jsonl"
    fill(EventLog(path))
    lines = path.read_text().splitlines()
    record = json.loads(lines[1])
    record["payload"]["text"] = "the well is full"
    lines[1] = json.dumps(record)
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(LogCorruptError):
        EventLog(path)


def test_deleted_event_is_detected(tmp_path):
    path = tmp_path / "v.jsonl"
    fill(EventLog(path))
    lines = path.read_text().splitlines()
    del lines[1]
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(LogCorruptError):
        EventLog(path)


def test_reordered_events_are_detected(tmp_path):
    path = tmp_path / "v.jsonl"
    fill(EventLog(path))
    lines = path.read_text().splitlines()
    lines[0], lines[1] = lines[1], lines[0]
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(LogCorruptError):
        EventLog(path)


def test_truncated_final_line_is_detected(tmp_path):
    path = tmp_path / "v.jsonl"
    fill(EventLog(path))
    path.write_bytes(path.read_bytes()[:-10])
    with pytest.raises(LogCorruptError):
        EventLog(path)


def test_dropped_tail_still_verifies_but_head_changes(tmp_path):
    path = tmp_path / "v.jsonl"
    log = EventLog(path)
    fill(log)
    full_head = log.head
    lines = path.read_text().splitlines()
    path.write_text("\n".join(lines[:2]) + "\n")
    assert EventLog(path).head != full_head


def test_unserialisable_payload_writes_nothing(tmp_path):
    path = tmp_path / "v.jsonl"
    log = EventLog(path)
    with pytest.raises(TypeError):
        log.append("saw", "ada", {"bad": object()})
    with pytest.raises(ValueError):
        log.append("saw", "ada", {"bad": float("nan")})
    assert len(log) == 0
    assert not path.exists() or path.read_bytes() == b""


@pytest.mark.parametrize("kind,writer", [("", "ada"), ("saw", "")])
def test_empty_kind_or_writer_is_rejected(tmp_path, kind, writer):
    log = EventLog(tmp_path / "v.jsonl")
    with pytest.raises(ValueError):
        log.append(kind, writer, {})
    assert len(log) == 0


@pytest.mark.parametrize("bad", ["not json", '{"id": 0}', "[1, 2]", '{"id": 0, "extra": 1}'])
def test_unreadable_records_are_detected(tmp_path, bad):
    path = tmp_path / "v.jsonl"
    path.write_text(bad + "\n")
    with pytest.raises(LogCorruptError):
        EventLog(path)
