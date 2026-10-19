"""The experimental arms. An arm is a memory admission policy plus a system prompt.

Arms differ only in these two values, which ``fork.fork`` takes, so every arm starts from
the same state and shares the same model, citizens, scheduler and loop. Changing an arm
changes the experiment: update the tests and the pre-registration first, and never after
runs start.

The shared base village runs as ``BASE`` until the planting event and the arms start at
the fork (ADR-0003).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent_village.admission import Admission, Claim, Event, admit, admit_corroborated
from agent_village.eventlog import EventLog, canonical_hash
from agent_village.memory import Policy
from agent_village.prompts import ANCHOR_SCRUTINY, BASELINE, Prompt


@dataclass(frozen=True)
class Arm:
    name: str
    policy: Policy
    prompt: Prompt
    settings: dict[str, Any] = field(default_factory=dict)
    """What parameterizes the policy, recorded at launch so an audit can tell arms apart."""


def admit_all(claim: Claim, evidence: dict[str, Event]) -> Admission:
    return Admission.FACT


@dataclass(frozen=True)
class RandomBlock:
    """Blocks a fixed share of claims, chosen by a hash of the claim and nothing else.

    A blocked claim is stored as hearsay, like a claim the kernel refuses, but the choice
    ignores provenance. Arm E sets ``rate`` to the share arm D blocks, so a difference
    between D and E is not just fewer writes. The same claim always gets the same decision.
    """

    rate: float
    salt: str

    def __post_init__(self) -> None:
        if not 0 <= self.rate <= 1:
            raise ValueError("rate must be between 0 and 1")

    def __call__(self, claim: Claim, evidence: dict[str, Event]) -> Admission:
        key = canonical_hash(
            {
                "salt": self.salt,
                "writer": claim.writer,
                "text": claim.text,
                "cites": list(claim.cites),
            }
        )
        blocked = int(key[:16], 16) / 16**16 < self.rate
        return Admission.HEARSAY if blocked else Admission.FACT


def random_block_arm(rate: float, salt: str) -> Arm:
    return Arm("E", RandomBlock(rate, salt), BASELINE, {"rate": rate, "salt": salt})


def matched_rate(log: EventLog, start: int) -> float:
    """The share of claims written from event ``start`` on that were stored as hearsay."""
    decisions = [e.payload["admission"] for e in log if e.kind == "claim" and e.id >= start]
    if not decisions:
        raise ValueError("the log has no claims to match")
    return decisions.count(Admission.HEARSAY.value) / len(decisions)


NO_DEFENSE = Arm("A", admit_all, BASELINE)
KERNEL_ADMISSION = Arm("D", admit, BASELINE)

PROMPT_DEFENSE = Arm("B", admit_all, ANCHOR_SCRUTINY[0])
"""Prompt-level anchoring plus source scrutiny: no memory policy, only a different prompt."""

PROMPT_DEFENSE_PARAPHRASES = (
    Arm("B2", admit_all, ANCHOR_SCRUTINY[1]),
    Arm("B3", admit_all, ANCHOR_SCRUTINY[2]),
)
"""The same defense in other words, run as the paraphrase control. Not in ``ARMS``."""

CORROBORATED = Arm("G", admit_corroborated, BASELINE)
"""Exploratory: the kernel, but the shared wiki also needs two independent sources, so a lone
first-hand witness cannot publish. Excluded from the primary contrast, like arm F."""

BASE = NO_DEFENSE

ARMS = {arm.name: arm for arm in (NO_DEFENSE, PROMPT_DEFENSE, KERNEL_ADMISSION, CORROBORATED)}
