import gc
import json
import random
import sqlite3
import warnings

import pytest
from villages import NAMES, drive, gossip, specs

from agent_village.arms import BASE, KERNEL_ADMISSION
from agent_village.eventlog import GENESIS, EventLog, LogCorruptError, digest
from agent_village.fork import build, fork
from agent_village.memory import Tier
from agent_village.model import FakeBackend
from agent_village.sqlitelog import (
    SCHEMA_VERSION,
    SqliteEventLog,
    WriterBusyError,
    jsonl_to_sqlite,
    sqlite_to_jsonl,
)

KINDS = [EventLog, SqliteEventLog]


def path_for(kind, tmp_path, name="v"):
    return tmp_path / (name + (".jsonl" if kind is EventLog else ".sqlite"))


@pytest.fixture(params=KINDS, ids=["jsonl", "sqlite"])
def kind(request):
    return request.param


def fill(log):
    log.append("saw", "ada", {"what": "well", "dry": True})
    log.append("told", "bo", {"to": "ada", "text": "the well is dry"})
    log.append("did", "ada", {"act": "fetch water"})


def test_both_stores_give_an_empty_log_the_genesis_head(kind, tmp_path):
    log = kind(path_for(kind, tmp_path))
    assert len(log) == 0 and log.head == GENESIS


def test_ids_are_sequential_and_the_chain_links(kind, tmp_path):
    log = kind(path_for(kind, tmp_path))
    fill(log)
    events = list(log)
    assert [e.id for e in events] == [0, 1, 2]
    assert events[0].prev == GENESIS and events[1].prev == events[0].hash
    assert log.head == events[2].hash and log[1] == events[1] and log[-1] == events[2]


def test_reopening_reproduces_the_events_and_continues_the_chain(kind, tmp_path):
    path = path_for(kind, tmp_path)
    log = kind(path)
    fill(log)
    before = list(log)
    if kind is SqliteEventLog:
        log.close()
    reopened = kind(path)
    assert list(reopened) == before
    assert reopened.append("did", "bo", {"act": "rest"}).prev == before[-1].hash


def test_the_payload_is_normalised_so_live_equals_loaded(kind, tmp_path):
    path = path_for(kind, tmp_path)
    log = kind(path)
    event = log.append("saw", "ada", {"seen": ("a", "b")})
    assert event.payload == {"seen": ["a", "b"]}
    if kind is SqliteEventLog:
        log.close()
    assert list(kind(path)) == [event]


def test_the_hash_vector_is_the_same_in_both_stores(kind, tmp_path):
    event = kind(path_for(kind, tmp_path)).append("saw", "ada", {"what": "well"})
    assert event.hash == "9a4a175c54059b8f226e5577429bed733ccd97f1fe3a5b5c2122d3a2912c4022"


def test_unserialisable_payloads_and_empty_names_write_nothing(kind, tmp_path):
    log = kind(path_for(kind, tmp_path))
    with pytest.raises(TypeError):
        log.append("saw", "ada", {"bad": object()})
    with pytest.raises(ValueError):
        log.append("saw", "ada", {"bad": float("nan")})
    for name, writer in (("", "ada"), ("saw", "")):
        with pytest.raises(ValueError):
            log.append(name, writer, {})
    assert len(log) == 0


def test_head_at_gives_the_head_after_any_prefix(kind, tmp_path):
    log = kind(path_for(kind, tmp_path))
    fill(log)
    assert log.head_at(0) == GENESIS and log.head_at(2) == log[1].hash
    assert log.head_at(3) == log.head
    for bad in (-1, 4):
        with pytest.raises(ValueError):
            log.head_at(bad)


def test_a_fork_copies_a_prefix_and_then_diverges(kind, tmp_path):
    log = kind(path_for(kind, tmp_path))
    fill(log)
    child = log.fork(path_for(kind, tmp_path, "child"), 2)
    assert type(child) is kind
    assert list(child) == list(log)[:2] and child.head == log.head_at(2)
    child.append("did", "bo", {"act": "other"})
    assert len(log) == 3 and len(child) == 3 and child.head != log.head
    whole = log.fork(path_for(kind, tmp_path, "whole"))
    assert list(whole) == list(log)


def test_a_fork_never_overwrites_a_file(kind, tmp_path):
    log = kind(path_for(kind, tmp_path))
    fill(log)
    target = path_for(kind, tmp_path, "child")
    target.write_bytes(b"")
    with pytest.raises(FileExistsError):
        log.fork(target)
    with pytest.raises(ValueError):
        log.fork(path_for(kind, tmp_path, "other"), 4)


def rows(path):
    connection = sqlite3.connect(path)
    try:
        return connection.execute("select id, payload from events order by id").fetchall()
    finally:
        connection.close()


def edit(path, sql, *args):
    connection = sqlite3.connect(path)
    connection.execute(sql, args)
    connection.commit()
    connection.close()


def closed_log(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    log = SqliteEventLog(path)
    fill(log)
    log.close()
    return path


def test_an_edited_payload_is_detected(tmp_path):
    path = closed_log(tmp_path)
    record = json.loads(rows(path)[1][1])
    record["text"] = "the well is full"
    edit(path, "update events set payload = ? where id = 1", json.dumps(record))
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_a_deleted_event_is_detected(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "delete from events where id = 1")
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_a_swapped_event_is_detected(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "update events set id = 9 where id = 0")
    edit(path, "update events set id = 0 where id = 1")
    edit(path, "update events set id = 1 where id = 9")
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_an_unreadable_row_is_detected(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "update events set payload = 'not json' where id = 2")
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_a_dropped_tail_still_verifies_but_the_head_changes(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    log = SqliteEventLog(path)
    fill(log)
    full = log.head
    log.close()
    edit(path, "delete from events where id = 2")
    assert SqliteEventLog(path).head != full


def test_the_database_runs_in_wal_mode_with_the_current_schema(tmp_path):
    path = closed_log(tmp_path)
    connection = sqlite3.connect(path)
    assert connection.execute("pragma journal_mode").fetchone()[0] == "wal"
    version = connection.execute("select value from meta where key = 'schema_version'").fetchone()
    assert int(version[0]) == SCHEMA_VERSION
    connection.close()


def test_an_older_schema_is_upgraded_in_place_without_losing_events(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "drop table claims")
    edit(path, "update meta set value = '0' where key = 'schema_version'")
    log = SqliteEventLog(path)
    assert [e.id for e in log] == [0, 1, 2]
    connection = sqlite3.connect(path)
    version = connection.execute("select value from meta where key = 'schema_version'").fetchone()
    assert int(version[0]) == SCHEMA_VERSION
    connection.execute("select * from claims").fetchall()
    connection.close()


def test_a_database_from_a_newer_harness_is_refused(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "update meta set value = ? where key = 'schema_version'", str(SCHEMA_VERSION + 1))
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_a_file_that_is_not_a_database_is_refused(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    path.write_bytes(b"this is not a database" * 50)
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_one_writer_per_village(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    first = SqliteEventLog(path)
    with pytest.raises(WriterBusyError):
        SqliteEventLog(path)
    first.close()
    second = SqliteEventLog(path)
    second.close()


def test_a_reader_can_open_a_log_a_writer_holds_but_cannot_append(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    writer = SqliteEventLog(path)
    fill(writer)
    reader = SqliteEventLog(path, readonly=True)
    assert list(reader) == list(writer)
    with pytest.raises(PermissionError):
        reader.append("did", "ada", {})
    writer.append("did", "bo", {"act": "rest"})
    assert len(reader) == 4
    reader.close()


def test_a_read_only_open_of_a_missing_file_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        SqliteEventLog(path_for(SqliteEventLog, tmp_path), readonly=True)


def test_closing_twice_is_harmless_and_a_closed_log_refuses_writes(tmp_path):
    log = SqliteEventLog(path_for(SqliteEventLog, tmp_path))
    log.close()
    log.close()
    with pytest.raises(ValueError):
        log.append("saw", "ada", {})


def test_the_context_manager_closes_the_log(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    with SqliteEventLog(path) as log:
        log.append("saw", "ada", {})
    SqliteEventLog(path).close()


def play(log, seed, ticks=14, policy=BASE.policy):
    world = build(log, random.Random(seed), FakeBackend(gossip), policy, BASE.prompt, specs(), 3)
    drive(world, ticks)
    return world


@pytest.mark.parametrize("seed", range(6))
def test_a_village_runs_to_the_same_events_and_hashes_on_either_store(tmp_path, seed):
    a = play(EventLog(path_for(EventLog, tmp_path)), seed)
    b = play(SqliteEventLog(path_for(SqliteEventLog, tmp_path)), seed)
    assert list(a.log) == list(b.log) and a.log.head == b.log.head


@pytest.mark.parametrize("seed", range(6))
def test_a_fork_on_the_sqlite_store_continues_like_the_base(tmp_path, seed):
    base = play(SqliteEventLog(path_for(SqliteEventLog, tmp_path)), seed, 8)
    branch = fork(
        base.snapshot(),
        base.log,
        path_for(SqliteEventLog, tmp_path, "fork"),
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        specs(),
        3,
    )
    drive(base, 6)
    drive(branch, 6)
    assert list(branch.log) == list(base.log)


def claims_of(log):
    return [
        (e.id, e.writer, e.payload["text"], e.payload["admission"], e.payload["stored"])
        for e in log
        if e.kind == "claim"
    ]


@pytest.mark.parametrize("seed", range(8))
def test_the_claims_projection_equals_memory_and_a_rebuild(tmp_path, seed):
    path = path_for(SqliteEventLog, tmp_path)
    world = play(SqliteEventLog(path), seed, 18, KERNEL_ADMISSION.policy)
    log = world.log
    live = log.claims()
    assert [(c.id, c.writer, c.text, c.admission, c.stored) for c in live] == claims_of(log)
    for tier in (Tier.CORE, Tier.RECALL):
        for name in NAMES:
            mine = tuple(e.id for e in world.memory.entries(tier, name))
            assert tuple(c.id for c in log.entries(tier.value, name)) == mine
    assert tuple(c.id for c in log.entries("shared")) == tuple(
        e.id for e in world.memory.entries(Tier.SHARED)
    )
    digest = log.projection_digest()
    log.rebuild_projections()
    assert log.claims() == live and log.projection_digest() == digest


def test_a_rebuild_repairs_a_projection_that_was_lost_or_changed(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    log = play(SqliteEventLog(path), 3, 18).log
    digest, live = log.projection_digest(), log.claims()
    assert live
    log.close()
    edit(path, "delete from claims")
    reopened = SqliteEventLog(path)
    assert reopened.projection_digest() != digest
    reopened.rebuild_projections()
    assert reopened.projection_digest() == digest and reopened.claims() == live


def test_an_unknown_tier_is_refused(tmp_path):
    log = SqliteEventLog(path_for(SqliteEventLog, tmp_path))
    with pytest.raises(ValueError):
        log.entries("archive")
    with pytest.raises(ValueError):
        log.entries("core")


def test_converting_a_jsonl_log_keeps_every_hash_and_the_bytes_round_trip(tmp_path):
    source = play(EventLog(path_for(EventLog, tmp_path)), 2, 12).log
    sqlite = jsonl_to_sqlite(path_for(EventLog, tmp_path), path_for(SqliteEventLog, tmp_path))
    assert list(sqlite) == list(source) and sqlite.head == source.head
    sqlite.close()
    back = tmp_path / "back.jsonl"
    sqlite_to_jsonl(path_for(SqliteEventLog, tmp_path), back)
    assert back.read_bytes() == path_for(EventLog, tmp_path).read_bytes()


def test_converting_refuses_to_overwrite(tmp_path):
    play(EventLog(path_for(EventLog, tmp_path)), 2, 3)
    target = path_for(SqliteEventLog, tmp_path)
    target.write_bytes(b"")
    with pytest.raises(FileExistsError):
        jsonl_to_sqlite(path_for(EventLog, tmp_path), target)
    existing = tmp_path / "out.jsonl"
    existing.write_bytes(b"")
    log = SqliteEventLog(tmp_path / "x.sqlite")
    log.close()
    with pytest.raises(FileExistsError):
        sqlite_to_jsonl(tmp_path / "x.sqlite", existing)


def raw_event(path, kind, writer, payload):
    """Append an event straight to the database, correctly chained, with no projection."""
    connection = sqlite3.connect(path)
    last = connection.execute("select id, hash from events order by id desc limit 1").fetchone()
    number, prev = (last[0] + 1, last[1]) if last else (0, GENESIS)
    connection.execute(
        "insert into events values (?,?,?,?,?,?)",
        (
            number,
            kind,
            writer,
            json.dumps(payload),
            prev,
            digest(number, kind, writer, payload, prev),
        ),
    )
    connection.commit()
    connection.close()


def test_an_event_row_outside_the_chain_is_detected(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "update events set id = -1 where id = 0")
    edit(path, "update events set id = 0 where id = 1")
    edit(path, "update events set id = 1 where id = 2")
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)
    edit(path, "delete from events")
    edit(path, "insert into events values (-1, 'saw', 'ada', '{}', 'x', 'y')")
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_a_failed_migration_changes_nothing(tmp_path):
    path = closed_log(tmp_path)
    raw_event(path, "claim", "ada", {})
    edit(path, "drop table claims")
    edit(path, "update meta set value = '0' where key = 'schema_version'")
    with pytest.raises(KeyError):
        SqliteEventLog(path)
    connection = sqlite3.connect(path)
    version = connection.execute("select value from meta where key = 'schema_version'").fetchone()
    assert version[0] == "0"
    assert connection.execute("select count(*) from events").fetchone()[0] == 4
    connection.close()
    SqliteEventLog(path, readonly=True).close()


def test_a_claim_event_without_its_fields_is_refused_and_leaves_the_log_usable(tmp_path):
    log = SqliteEventLog(path_for(SqliteEventLog, tmp_path))
    fill(log)
    with pytest.raises(KeyError):
        log.append("claim", "ada", {"text": "no other fields"})
    assert len(log) == 3
    assert log.append("did", "ada", {}).id == 3
    log.close()
    assert len(SqliteEventLog(path_for(SqliteEventLog, tmp_path))) == 4


def test_a_fork_that_fails_leaves_no_writer_holding_the_child(tmp_path):
    path = closed_log(tmp_path)
    raw_event(path, "claim", "ada", {})
    log = SqliteEventLog(path)
    child = path_for(SqliteEventLog, tmp_path, "child")
    with pytest.raises(KeyError):
        log.fork(child)
    SqliteEventLog(child).close()


def test_a_failed_rebuild_keeps_the_projection_it_had(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    log = play(SqliteEventLog(path), 3, 18).log
    before = log.projection_digest()
    log.close()
    raw_event(path, "claim", "ada", {})
    reopened = SqliteEventLog(path)
    with pytest.raises(KeyError):
        reopened.rebuild_projections()
    assert reopened.projection_digest() == before


def test_a_reader_cannot_rebuild(tmp_path):
    path = closed_log(tmp_path)
    reader = SqliteEventLog(path, readonly=True)
    with pytest.raises(PermissionError):
        reader.rebuild_projections()
    reader.close()


def test_a_conversion_that_fails_leaves_no_writer_holding_the_database(tmp_path):
    source = path_for(EventLog, tmp_path)
    log = EventLog(source)
    fill(log)
    log.append("claim", "ada", {"text": "no other fields"})
    with pytest.raises(KeyError):
        jsonl_to_sqlite(source, path_for(SqliteEventLog, tmp_path))
    SqliteEventLog(path_for(SqliteEventLog, tmp_path)).close()


def test_dropping_a_log_without_closing_it_releases_the_writer(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    log = SqliteEventLog(path)
    log.append("saw", "ada", {})
    del log
    gc.collect()
    SqliteEventLog(path).close()


def test_an_altered_prev_column_is_detected_even_when_the_hash_still_matches(tmp_path):
    path = closed_log(tmp_path)
    edit(path, "update events set prev = 'x' where id = 1")
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_a_forged_event_that_skips_an_id_is_detected(tmp_path):
    path = closed_log(tmp_path)
    connection = sqlite3.connect(path)
    first = connection.execute("select hash from events where id = 0").fetchone()[0]
    connection.execute("delete from events where id > 0")
    forged = digest(5, "saw", "ada", {}, first)
    connection.execute("insert into events values (5, 'saw', 'ada', '{}', ?, ?)", (first, forged))
    connection.commit()
    connection.close()
    with pytest.raises(LogCorruptError):
        SqliteEventLog(path)


def test_dropping_an_open_log_raises_no_resource_warning(tmp_path):
    path = path_for(SqliteEventLog, tmp_path)
    log = SqliteEventLog(path)
    log.append("saw", "ada", {})
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        del log
        gc.collect()
    assert not [w for w in caught if issubclass(w.category, ResourceWarning)]
