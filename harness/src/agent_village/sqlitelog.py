"""The event log in SQLite: one file per village, write-ahead logging, rebuildable projections.

``SqliteEventLog`` keeps the same contract as the JSONL ``EventLog`` (ADR-0001): append-only,
hash-chained, verified when opened, forked by prefix, and byte-for-byte the same events and hashes,
so a village runs identically on either store. Beside the ``events`` table it keeps a ``claims``
projection that is written in the same transaction as the claim event and can be rebuilt from the
events alone; the tiers are that table seen by ``stored``. Schema changes are additive migrations
recorded in ``meta``.

One writer per village: opening for writing takes an exclusive lock on ``<file>.lock`` and a second
writer is refused (``WriterBusyError``). A reader may open a log a writer holds and sees what the
writer has committed.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import sqlite3
import threading
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

from agent_village.eventlog import (
    GENESIS,
    EventLog,
    LogCorruptError,
    LogEvent,
    digest,
    normalise,
)

SCHEMA_VERSION = 1

_MIGRATIONS = (
    """
    create table if not exists events (
        id integer primary key,
        kind text not null,
        writer text not null,
        payload text not null,
        prev text not null,
        hash text not null
    );
    create table if not exists claims (
        id integer primary key references events(id),
        writer text not null,
        text text not null,
        kind text not null,
        cites text not null,
        requested text not null,
        admission text not null,
        stored text not null
    );
    create index if not exists claims_by_tier on claims(stored, writer);
    """,
)

_TIERS = ("core", "recall", "shared")
_CLAIM_COLUMNS = "id, writer, text, kind, cites, requested, admission, stored"


class WriterBusyError(Exception):
    """Another writer holds this village's log."""


@dataclass(frozen=True)
class ClaimRow:
    """A claim as the projection stores it: what was written and how admission decided."""

    id: int
    writer: str
    text: str
    kind: str
    cites: tuple[str, ...]
    requested: str
    admission: str
    stored: str


def _claim_row(event: LogEvent) -> tuple[Any, ...]:
    p = event.payload
    return (
        event.id,
        event.writer,
        p["text"],
        p["kind"],
        json.dumps(p["cites"]),
        p["requested"],
        p["admission"],
        p["stored"],
    )


class SqliteEventLog:
    def __init__(self, path: Path | str, readonly: bool = False) -> None:
        self._path = Path(path)
        self._readonly = readonly
        self._events: list[LogEvent] = []
        self._guard = threading.RLock()
        self._lock_file: IO[str] | None = None
        self._connection: sqlite3.Connection | None = None
        if readonly and not self._path.exists():
            raise FileNotFoundError(str(self._path))
        if not readonly:
            self._take_writer_lock()
        try:
            self._connection = sqlite3.connect(
                f"file:{self._path}?mode={'ro' if readonly else 'rwc'}",
                uri=True,
                check_same_thread=False,
                isolation_level=None,
            )
            self._open()
        except sqlite3.DatabaseError as error:
            self.close()
            raise LogCorruptError(f"{self._path}: not a readable event database") from error
        except Exception:
            self.close()
            raise

    def _take_writer_lock(self) -> None:
        handle = open(f"{self._path}.lock", "w")  # noqa: SIM115 - held until close()
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            raise WriterBusyError(f"{self._path} already has a writer") from None
        self._lock_file = handle

    def _open(self) -> None:
        db = self._db
        if not self._readonly:
            db.execute("pragma journal_mode = wal")
            db.execute("pragma synchronous = full")
            self._migrate()
        self._events = []
        self._load()

    @property
    def _db(self) -> sqlite3.Connection:
        if self._connection is None:
            raise ValueError("the log is closed")
        return self._connection

    def _version(self) -> int:
        db = self._db
        db.execute("create table if not exists meta (key text primary key, value text not null)")
        row = db.execute("select value from meta where key = 'schema_version'").fetchone()
        return int(row[0]) if row else 0

    def _migrate(self) -> None:
        version = self._version()
        if version > SCHEMA_VERSION:
            raise LogCorruptError(
                f"{self._path}: schema {version} is newer than this harness knows ({SCHEMA_VERSION})"
            )
        if version == SCHEMA_VERSION:
            return
        db = self._db
        db.execute("begin immediate")
        try:
            for script in _MIGRATIONS[version:]:
                for statement in script.split(";"):
                    if statement.strip():
                        db.execute(statement)
            db.execute(
                "insert or replace into meta(key, value) values ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
            self._rebuild(db)
            db.execute("commit")
        except BaseException:
            db.execute("rollback")
            raise

    def _load(self) -> None:
        prev = self._events[-1].hash if self._events else GENESIS
        cursor = self._db.execute(
            "select id, kind, writer, payload, prev, hash from events where id >= ? order by id",
            (len(self._events),),
        )
        for number, (id_, kind, writer, payload, before, hash_) in enumerate(
            cursor, start=len(self._events)
        ):
            try:
                body = json.loads(payload)
            except ValueError as error:
                raise LogCorruptError(f"event {number}: unreadable payload") from error
            if id_ != number or before != prev or hash_ != digest(id_, kind, writer, body, prev):
                raise LogCorruptError(f"event {number}: hash chain broken")
            self._events.append(LogEvent(id_, kind, writer, body, before, hash_))
            prev = hash_
        if self._db.execute("select count(*) from events").fetchone()[0] != len(self._events):
            raise LogCorruptError("the events table has a gap or a row out of order")

    def _refresh(self) -> None:
        if self._readonly:
            with self._guard:
                self._load()

    @property
    def head(self) -> str:
        self._refresh()
        return self._events[-1].hash if self._events else GENESIS

    def append(self, kind: str, writer: str, payload: Mapping[str, Any]) -> LogEvent:
        if self._readonly:
            raise PermissionError("this log was opened read-only")
        if not kind or not writer:
            raise ValueError("kind and writer must be non-empty")
        body = normalise(payload)
        with self._guard:
            db = self._db
            number = len(self._events)
            prev = self._events[-1].hash if self._events else GENESIS
            event = LogEvent(
                number, kind, writer, body, prev, digest(number, kind, writer, body, prev)
            )
            db.execute("begin immediate")
            try:
                db.execute(
                    "insert into events(id, kind, writer, payload, prev, hash) values (?,?,?,?,?,?)",
                    (
                        number,
                        kind,
                        writer,
                        json.dumps(body, sort_keys=True, ensure_ascii=False),
                        prev,
                        event.hash,
                    ),
                )
                if kind == "claim":
                    db.execute(
                        f"insert into claims({_CLAIM_COLUMNS}) values (?,?,?,?,?,?,?,?)",
                        _claim_row(event),
                    )
                db.execute("commit")
            except BaseException:
                db.execute("rollback")
                raise
            self._events.append(event)
            return event

    def head_at(self, count: int) -> str:
        """The head hash after the first ``count`` events."""
        self._refresh()
        if not 0 <= count <= len(self._events):
            raise ValueError(f"the log has {len(self._events)} events, not {count}")
        return self._events[count - 1].hash if count else GENESIS

    def fork(self, dest: Path | str, upto: int | None = None) -> SqliteEventLog:
        """Copy the first ``upto`` events (default all) into a new database."""
        self._refresh()
        count = len(self._events) if upto is None else upto
        self.head_at(count)
        if Path(dest).exists():
            raise FileExistsError(str(dest))
        child = SqliteEventLog(dest)
        try:
            for event in self._events[:count]:
                child.append(event.kind, event.writer, event.payload)
        except BaseException:
            child.close()
            raise
        return child

    def claims(self) -> list[ClaimRow]:
        """Every claim the projection holds, in the order they were written."""
        return self._rows("select " + _CLAIM_COLUMNS + " from claims order by id")

    def entries(self, tier: str, writer: str | None = None) -> list[ClaimRow]:
        """The claims stored in ``tier``; core and recall are private, so they need their writer."""
        if tier not in _TIERS:
            raise ValueError(f"unknown tier {tier!r}")
        if tier == "shared":
            return self._rows(
                f"select {_CLAIM_COLUMNS} from claims where stored = ? order by id", (tier,)
            )
        if writer is None:
            raise ValueError(f"the {tier} tier is private: name its writer")
        return self._rows(
            f"select {_CLAIM_COLUMNS} from claims where stored = ? and writer = ? order by id",
            (tier, writer),
        )

    def _rows(self, sql: str, args: tuple[Any, ...] = ()) -> list[ClaimRow]:
        self._refresh()
        with self._guard:
            found = self._db.execute(sql, args).fetchall()
        return [
            ClaimRow(
                id_, writer, text, kind, tuple(json.loads(cites)), requested, admission, stored
            )
            for id_, writer, text, kind, cites, requested, admission, stored in found
        ]

    def projection_digest(self) -> str:
        """A hash of the claims projection, to compare a live one with a rebuilt one."""
        text = json.dumps([list(map(str, _row_tuple(c))) for c in self.claims()])
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def rebuild_projections(self) -> None:
        """Recompute every projection from the events alone."""
        if self._readonly:
            raise PermissionError("this log was opened read-only")
        with self._guard:
            db = self._db
            db.execute("begin immediate")
            try:
                self._rebuild(db)
                db.execute("commit")
            except BaseException:
                db.execute("rollback")
                raise

    def _rebuild(self, db: sqlite3.Connection) -> None:
        db.execute("delete from claims")
        for event in self._events_from(db):
            if event.kind == "claim":
                db.execute(
                    f"insert into claims({_CLAIM_COLUMNS}) values (?,?,?,?,?,?,?,?)",
                    _claim_row(event),
                )

    def _events_from(self, db: sqlite3.Connection) -> Iterator[LogEvent]:
        for id_, kind, writer, payload, prev, hash_ in db.execute(
            "select id, kind, writer, payload, prev, hash from events order by id"
        ):
            yield LogEvent(id_, kind, writer, json.loads(payload), prev, hash_)

    def close(self) -> None:
        with self._guard:
            if self._connection is not None:
                self._connection.close()
                self._connection = None
            if self._lock_file is not None:
                self._lock_file.close()
                self._lock_file = None

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> SqliteEventLog:  # noqa: PYI034 - Self needs Python 3.11
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def __len__(self) -> int:
        self._refresh()
        return len(self._events)

    def __iter__(self) -> Iterator[LogEvent]:
        self._refresh()
        return iter(list(self._events))

    def __getitem__(self, index: int) -> LogEvent:
        self._refresh()
        return self._events[index]


def _row_tuple(c: ClaimRow) -> tuple[Any, ...]:
    return (c.id, c.writer, c.text, c.kind, list(c.cites), c.requested, c.admission, c.stored)


def jsonl_to_sqlite(source: Path | str, dest: Path | str) -> SqliteEventLog:
    """Copy a JSONL log into a new database, keeping every event and hash."""
    if Path(dest).exists():
        raise FileExistsError(str(dest))
    original = EventLog(source)
    log = SqliteEventLog(dest)
    try:
        for event in original:
            log.append(event.kind, event.writer, event.payload)
    except BaseException:
        log.close()
        raise
    return log


def sqlite_to_jsonl(source: Path | str, dest: Path | str) -> EventLog:
    """Write a database's events as a JSONL log, byte for byte as the JSONL store would."""
    with SqliteEventLog(source, readonly=True) as log:
        lines = [json.dumps(e.__dict__, sort_keys=True, ensure_ascii=False) + "\n" for e in log]
    with Path(dest).open("x", encoding="utf-8") as handle:
        handle.writelines(lines)
    return EventLog(dest)
