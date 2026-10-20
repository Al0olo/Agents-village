"""Planning the number of blocks: the power of the paired sign-flip test by simulation.

The registered test is the exact sign-flip test (``analysis.sign_flip_test``). To plan, the
paired differences of a contrast are drawn from a normal distribution with the assumed mean
effect and spread across blocks, and the share of draws the test rejects at ``alpha`` is the
power. Above ``exact_up_to`` blocks the p-value is a Monte Carlo estimate over random sign
patterns (the observed pattern counted, so it is never zero), which is close to the exact one
and fast enough to scan block counts. Pure and seeded: the same arguments give the same number.
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from agent_village.analysis import flip_estimate, sign_flip_test

EXACT_UP_TO = 16


def sign_flip_p(
    differences: Sequence[float], flips: int, seed: int, exact_up_to: int = EXACT_UP_TO
) -> float:
    """The exact sign-flip p-value for small samples, else a Monte Carlo estimate."""
    if len(differences) <= exact_up_to:
        return sign_flip_test(differences)
    return flip_estimate(differences, flips, seed)


def power(
    effect: float,
    spread: float,
    blocks: int,
    seed: int,
    reps: int = 1000,
    alpha: float = 0.05,
    flips: int = 499,
) -> float:
    """The share of simulated experiments of ``blocks`` blocks that the test rejects."""
    if spread <= 0 or blocks < 1 or reps < 1 or not 0 < alpha < 1:
        raise ValueError("spread and alpha must be positive, blocks and reps at least 1")
    rng = random.Random(f"{seed}:{effect}:{spread}:{blocks}")
    rejected = 0
    for rep in range(reps):
        differences = [rng.gauss(effect, spread) for _ in range(blocks)]
        if sign_flip_p(differences, flips, seed * 100003 + rep) < alpha:
            rejected += 1
    return rejected / reps


def blocks_needed(
    effect: float,
    spread: float,
    seed: int,
    target: float = 0.8,
    reps: int = 1000,
    alpha: float = 0.05,
    limit: int = 60,
) -> int | None:
    """The fewest blocks, up to ``limit``, whose power reaches ``target``; None if even ``limit`` does not.

    Found by bisection, which takes power to rise with the number of blocks; the result is a block
    count ``n`` for which power reaches the target and that of ``n - 1`` does not.
    """
    if not 0 < target < 1:
        raise ValueError("the target power must be between 0 and 1")

    def enough(blocks: int) -> bool:
        return power(effect, spread, blocks, seed, reps, alpha) >= target

    low, high = 3, limit
    if enough(low):
        return low
    if not enough(high):
        return None
    while high - low > 1:
        middle = (low + high) // 2
        if enough(middle):
            high = middle
        else:
            low = middle
    return high
