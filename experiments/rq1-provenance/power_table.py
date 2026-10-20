"""How many blocks the main run needs, for assumed effects and block-to-block spreads.

    python experiments/rq1-provenance/power_table.py [--observed BLOCK_DIR...] [--arm D --against A]

Prints, for each assumed effect (the true mean paired difference in the assertion rate of false
facts) and spread (the standard deviation of that difference across blocks), the fewest blocks at
which the paired sign-flip test reaches 80% power at alpha 0.05, by simulation
(``agent_village.power``). With ``--observed`` it also prints the spread actually seen in the
finished blocks, from ``analyze_blocks.block_measures``. A spread from two to five blocks is a
rough number; it is a planning input, not a result.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_village.power import blocks_needed

EFFECTS = (0.10, 0.15, 0.20, 0.30)
SPREADS = (0.10, 0.20, 0.30, 0.40)


def observed_spread(
    blocks: list[str], arm: str, against: str, measure: str
) -> tuple[list[float], float]:
    from analyze_blocks import block_measures

    differences = []
    for directory in blocks:
        measures = block_measures(Path(directory))
        if arm in measures and against in measures:
            a, b = getattr(measures[arm], measure), getattr(measures[against], measure)
            if a is not None and b is not None:
                differences.append(a - b)
    return differences, statistics.stdev(differences) if len(differences) > 1 else float("nan")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed", nargs="*", default=[])
    parser.add_argument("--arm", default="D")
    parser.add_argument("--against", default="A")
    parser.add_argument("--measure", default="attack_rate")
    parser.add_argument("--reps", type=int, default=600)
    args = parser.parse_args()
    if args.observed:
        differences, spread = observed_spread(args.observed, args.arm, args.against, args.measure)
        shown = ", ".join(f"{d:+.2f}" for d in differences)
        print(f"{args.arm} minus {args.against} over {len(differences)} blocks: {shown}")
        print(f"mean {statistics.fmean(differences):+.2f}, spread (sample sd) {spread:.2f}\n")
    print("blocks for 80% power at alpha 0.05 (rows: assumed spread; columns: assumed effect)")
    print("spread  " + "".join(f"{e:>8.2f}" for e in EFFECTS))
    for spread in SPREADS:
        cells = []
        for effect in EFFECTS:
            n = blocks_needed(effect, spread, seed=1, reps=args.reps, limit=80)
            cells.append(f"{n:>8}" if n is not None else "    >80 ")
        print(f"{spread:<8.2f}" + "".join(cells))


if __name__ == "__main__":
    main()
