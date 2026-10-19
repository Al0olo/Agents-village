"""Reference implementation of the RQ1 kernel admission policy.

A claim reaches core or shared memory as *fact* only if it cites

* at least one first-hand event in the writer's own log (an observation, an
  action the writer took, a tool receipt or a ledger entry), or
* at least two told-events whose origin sets are disjoint, where the origin is
  the root source the kernel tracks through every forward. A told-event whose
  origins include the writer is the writer's own claim coming back and does not
  count.

Everything else is stored as *hearsay* in recall. The policy checks citation
provenance, not truth, and no model is involved in the decision.

``admit_corroborated`` is the stricter policy of the exploratory arm: a claim for the
shared tier needs two independent sources even when the writer saw it first-hand, because a
lone witness is also how a false fact gets published. It never admits what ``admit`` would
refuse, and it treats a private claim exactly as ``admit`` does.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Kind(str, Enum):
    SEEN = "seen"
    DID = "did"
    TOLD = "told"


class Admission(str, Enum):
    FACT = "fact"
    HEARSAY = "hearsay"


@dataclass(frozen=True)
class Event:
    id: str
    writer: str
    kind: Kind
    origins: frozenset[str] = frozenset()
    """Root sources of the information. Empty for first-hand events."""


@dataclass(frozen=True)
class Claim:
    text: str
    writer: str
    cites: tuple[str, ...]
    shared: bool = False
    """Whether the writer asks for the shared tier."""


def admit(claim: Claim, log: dict[str, Event]) -> Admission:
    """Decide whether ``claim`` is admitted as fact. Pure and deterministic."""
    cited = [log[c] for c in claim.cites if c in log and log[c].writer == claim.writer]

    if any(e.kind in (Kind.SEEN, Kind.DID) for e in cited):
        return Admission.FACT

    told = [e for e in cited if e.kind is Kind.TOLD and e.origins and claim.writer not in e.origins]
    for i, a in enumerate(told):
        for b in told[i + 1 :]:
            if a.origins.isdisjoint(b.origins):
                return Admission.FACT
    return Admission.HEARSAY


def admit_corroborated(claim: Claim, log: dict[str, Event]) -> Admission:
    """Like ``admit``, but a shared-tier claim needs two sources with disjoint origins.

    A first-hand event is a source whose origin is the writer. A told-event is a source
    whose origins are its own, and one that traces back to the writer does not count.
    """
    if not claim.shared:
        return admit(claim, log)
    sources = []
    for cite in claim.cites:
        event = log.get(cite)
        if event is None or event.writer != claim.writer:
            continue
        if event.kind in (Kind.SEEN, Kind.DID):
            sources.append(frozenset({claim.writer}))
        elif event.origins and claim.writer not in event.origins:
            sources.append(event.origins)
    for i, a in enumerate(sources):
        if any(a.isdisjoint(b) for b in sources[i + 1 :]):
            return Admission.FACT
    return Admission.HEARSAY
