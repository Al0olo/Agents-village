"""The review pass at the end of a simulated day (ADR-0013).

Like a probe round it is one driver action between ticks: a ``consolidation`` marker holding
the review prompt, then for each citizen a ``model_call``, the ``claim`` events of its notes
and a ``review`` event. Audit replay reproduces it from the marker. Every note goes through
the arm's memory policy, so the pass is not a way around admission.
"""

from __future__ import annotations

from agent_village.fork import ENVIRONMENT, World
from agent_village.prompts import Prompt

CONSOLIDATION = "consolidation"


def run_consolidation(world: World, prompt: Prompt) -> None:
    if world.village.state().awake:
        raise ValueError("a review is run between ticks")
    world.log.append(
        CONSOLIDATION, ENVIRONMENT, {"prompt_version": prompt.version, "prompt_hash": prompt.hash}
    )
    for name in world.village.state().citizens:
        world.runner.review(name, prompt)
