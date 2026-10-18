"""Reference implementation of the RQ1 kernel admission policy.

A claim reaches core or shared memory as *fact* only if it cites

* at least one first-hand event in the writer's own log (an observation, an
  action the writer took, a tool receipt or a ledger entry), or
* at least two told-events whose origin sets are disjoint, where the origin is
  the root source the kernel tracks through every forward.

Everything else is stored as *hearsay* in recall. The policy checks citation
provenance, not truth, and no model is involved in the decision.
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


def admit(claim: Claim, log: dict[str, Event]) -> Admission:
    """Decide whether ``claim`` is admitted as fact. Pure and deterministic."""
    cited = [log[c] for c in claim.cites if c in log and log[c].writer == claim.writer]

    if any(e.kind in (Kind.SEEN, Kind.DID) for e in cited):
        return Admission.FACT

    told = [e for e in cited if e.kind is Kind.TOLD and e.origins]
    for i, a in enumerate(told):
        for b in told[i + 1 :]:
            if a.origins.isdisjoint(b.origins):
                return Admission.FACT
    return Admission.HEARSAY
