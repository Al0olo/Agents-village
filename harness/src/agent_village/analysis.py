"""The pre-registered analysis of paired blocks: differences, an exact test, intervals, Holm.

The unit is the block. For each block an arm's outcome is one number, and a contrast is the
difference between two arms in the same block. A two-sided exact sign-flip test asks how often
random signs on the differences give a mean at least as far from zero as the observed one; with
n blocks the smallest possible p is 2 / 2**n, so ten paired blocks can reach about 0.002 where
four unpaired villages per arm cannot go below 0.029. Intervals are percentile bootstrap
intervals over blocks. Holm's step-down method adjusts a family of p-values.
"""

from __future__ import annotations

import itertools
import random
import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

MAX_EXACT = 20


def paired_differences(
    values: Mapping[int, Mapping[str, float]], first: str, second: str
) -> dict[int, float]:
    """``first`` minus ``second`` in every block that has both arms."""
    return {
        block: arms[first] - arms[second]
        for block, arms in sorted(values.items())
        if first in arms and second in arms
    }


def sign_flip_test(differences: Sequence[float]) -> float:
    """Two-sided exact p-value that the mean difference is zero."""
    if not differences:
        raise ValueError("a test needs at least one difference")
    if len(differences) > MAX_EXACT:
        raise ValueError(f"exact enumeration is limited to {MAX_EXACT} blocks")
    observed = abs(sum(differences))
    tolerance = 1e-12
    extreme = total = 0
    for signs in itertools.product((1, -1), repeat=len(differences)):
        total += 1
        if abs(sum(s * d for s, d in zip(signs, differences, strict=True))) >= observed - tolerance:
            extreme += 1
    return extreme / total


@dataclass(frozen=True)
class Contrast:
    first: str
    second: str
    blocks: int
    mean_difference: float
    p: float
    interval: tuple[float, float]
    dz: float | None


def contrast(
    values: Mapping[int, Mapping[str, float]], first: str, second: str, seed: int
) -> Contrast:
    """One registered contrast: the paired difference, its exact p, interval and effect size."""
    diffs = list(paired_differences(values, first, second).values())
    if not diffs:
        raise ValueError(f"no block has both {first} and {second}")
    return Contrast(
        first,
        second,
        len(diffs),
        statistics.fmean(diffs),
        sign_flip_test(diffs),
        bootstrap_interval(diffs, seed),
        cohens_dz(diffs),
    )


def cohens_dz(differences: Sequence[float]) -> float | None:
    """The mean difference over its sample standard deviation, or None if that is zero or undefined."""
    if len(differences) < 2:
        return None
    spread = statistics.stdev(differences)
    return statistics.fmean(differences) / spread if spread > 0 else None


def bootstrap_interval(
    differences: Sequence[float], seed: int, level: float = 0.95, reps: int = 10000
) -> tuple[float, float]:
    """A percentile bootstrap interval for the mean difference, resampling blocks."""
    if not differences:
        raise ValueError("an interval needs at least one difference")
    if not 0 < level < 1:
        raise ValueError("level must be between 0 and 1")
    rng = random.Random(f"{seed}:bootstrap")
    n = len(differences)
    means = sorted(statistics.fmean(rng.choices(differences, k=n)) for _ in range(reps))
    tail = (1 - level) / 2
    return means[int(tail * reps)], means[min(int((1 - tail) * reps), reps - 1)]


def holm(pvalues: Mapping[str, float]) -> dict[str, float]:
    """Holm's step-down adjustment: the smallest p is multiplied by the family size, and so on."""
    if any(not 0 <= p <= 1 for p in pvalues.values()):
        raise ValueError("p-values must be between 0 and 1")
    ordered = sorted(pvalues, key=lambda name: pvalues[name])
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, name in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - rank) * pvalues[name]))
        adjusted[name] = running
    return adjusted
