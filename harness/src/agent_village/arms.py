"""The experimental arms. An arm is a memory admission policy plus a system prompt.

Arms differ only in these two values, which ``fork.fork`` takes, so every arm starts from
the same state and shares the same model, citizens, scheduler and loop. Changing an arm
changes the experiment: update the tests and the pre-registration first, and never after
runs start.

The shared base village runs as ``BASE`` until the planting event and the arms start at
the fork (ADR-0003).
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_village.admission import Admission, Claim, Event, admit
from agent_village.memory import Policy
from agent_village.prompts import BASELINE, Prompt


@dataclass(frozen=True)
class Arm:
    name: str
    policy: Policy
    prompt: Prompt


def admit_all(claim: Claim, evidence: dict[str, Event]) -> Admission:
    return Admission.FACT


NO_DEFENSE = Arm("A", admit_all, BASELINE)
KERNEL_ADMISSION = Arm("D", admit, BASELINE)

BASE = NO_DEFENSE

ARMS = {arm.name: arm for arm in (NO_DEFENSE, KERNEL_ADMISSION)}
