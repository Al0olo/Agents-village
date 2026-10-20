"""Memory tiers as a projection of the event log, with structured claim writes.

A claim write carries text, a declared kind and cited event ids. The injected policy
decides fact or hearsay from the cited events, never from the declared kind. A fact is
stored in the tier it asked for, core (private) or shared (the village wiki); anything
else is stored as hearsay in the writer's recall. The decision is logged, so the state
rebuilds from the log without running the policy again.

Evidence comes from log events of kind ``saw`` and ``did`` (written by the citizen) and
``told`` (written by the recipient, with ``origins`` in the payload) and ``heard`` (a rumor a
traveler told a citizen, which is ``told`` evidence with an origin of its own). No other event kind
is evidence, claims included.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from agent_village.admission import Admission, Claim, Event, Kind
from agent_village.eventlog import EventLog

Policy = Callable[[Claim, dict[str, Event]], Admission]

_EVIDENCE = {"saw": Kind.SEEN, "did": Kind.DID, "told": Kind.TOLD, "heard": Kind.TOLD}


class Tier(str, Enum):
    CORE = "core"
    RECALL = "recall"
    SHARED = "shared"


@dataclass(frozen=True)
class Entry:
    id: int
    writer: str
    text: str
    kind: Kind
    cites: tuple[str, ...]
    requested: Tier
    admission: Admission
    tier: Tier


class Memory:
    def __init__(self, log: EventLog, policy: Policy) -> None:
        self._log = log
        self._policy = policy
        self._evidence: dict[str, Event] = {}
        self._entries: list[Entry] = []
        self._cursor = 0
        self._sync()

    def write_claim(
        self, writer: str, text: str, kind: Kind, cites: tuple[str, ...], tier: Tier
    ) -> Entry:
        if not writer or not text:
            raise ValueError("writer and text must be non-empty")
        if tier not in (Tier.CORE, Tier.SHARED):
            raise ValueError("claims are written to core or shared memory")
        self._sync()
        decision = self._policy(Claim(text, writer, cites, tier is Tier.SHARED), self._evidence)
        stored = tier if decision is Admission.FACT else Tier.RECALL
        self._log.append(
            "claim",
            writer,
            {
                "text": text,
                "kind": kind.value,
                "cites": list(cites),
                "requested": tier.value,
                "admission": decision.value,
                "stored": stored.value,
            },
        )
        self._sync()
        return self._entries[-1]

    def entries(self, tier: Tier, writer: str | None = None) -> tuple[Entry, ...]:
        """Entries in ``tier``; core and recall are private, so they need their ``writer``."""
        self._sync()
        if tier is Tier.SHARED:
            return tuple(e for e in self._entries if e.tier is tier)
        return tuple(e for e in self._entries if e.tier is tier and e.writer == writer)

    def _sync(self) -> None:
        while self._cursor < len(self._log):
            event = self._log[self._cursor]
            self._cursor += 1
            if event.kind in _EVIDENCE:
                kind = _EVIDENCE[event.kind]
                origins = event.payload.get("origins", ()) if kind is Kind.TOLD else ()
                key = str(event.id)
                self._evidence[key] = Event(key, event.writer, kind, frozenset(origins))
            elif event.kind == "claim":
                p = event.payload
                self._entries.append(
                    Entry(
                        event.id,
                        event.writer,
                        p["text"],
                        Kind(p["kind"]),
                        tuple(p["cites"]),
                        Tier(p["requested"]),
                        Admission(p["admission"]),
                        Tier(p["stored"]),
                    )
                )
