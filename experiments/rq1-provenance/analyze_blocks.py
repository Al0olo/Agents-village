"""Per-block measures and paired contrasts over finished blocks, offline.

    python experiments/rq1-provenance/analyze_blocks.py BLOCK_DIR... [--against A] [--judge 1|2]

Each ``BLOCK_DIR`` is named ``block-N`` and holds the arm logs and ``judge.jsonl`` (judge 1, the primary) and
``judge2.jsonl`` (judge 2, for the sensitivity analysis). The judge's
replies are read back through ``replay_codes``, so no model is called. For every measure it
prints the value per block and arm, then each arm's paired difference from ``--against``
over the blocks that have both, with the exact sign-flip test, a bootstrap interval and
Cohen's dz (``analysis.contrast``). With few blocks the test cannot go below p = 2 / 2**n,
so read the differences and intervals, not the p-values.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness" / "src"))

from agent_village.analysis import contrast
from agent_village.eventlog import EventLog
from agent_village.judge import attach, blind, collect, replay_codes
from agent_village.metrics import Metrics, compute

JUDGES = {
    1: ("judge.jsonl", "anthropic/claude-haiku-5.5"),
    2: ("judge2.jsonl", "openai/gpt-5.6-sol"),
}
BLIND_SEED = 7
SMALL = 10
MEASURES = (
    "attack_rate_rumor",
    "attack_rate_witness",
    "attack_rate",
    "carry_rate",
    "wiki_contamination",
    "true_acceptance",
    "true_carry_rate",
    "utility_score",
    "awareness_rate",
)


def block_measures(directory: Path, judge: int = 1) -> dict[str, Metrics]:
    name, model = JUDGES[judge]
    arms = [
        p.stem
        for p in sorted(directory.glob("*.jsonl"))
        if p.stem not in ("base", "judge", "judge2")
    ]
    logs = {(0, arm): EventLog(directory / f"{arm}.jsonl") for arm in arms}
    blinded = blind(collect(logs), BLIND_SEED)
    with tempfile.TemporaryDirectory() as scratch:
        codes, _ = replay_codes(blinded.items, EventLog(directory / name), model, Path(scratch))
    coded = attach(blinded, codes)
    return {arm: compute(logs[(0, arm)], coded, 0, arm) for arm in arms}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("blocks", nargs="+")
    parser.add_argument("--against", default="A")
    parser.add_argument("--judge", type=int, choices=sorted(JUDGES), default=1)
    args = parser.parse_args()
    by_block = {
        int(Path(b).name.split("-")[-1]): block_measures(Path(b), args.judge) for b in args.blocks
    }
    for measure in MEASURES:
        values = {
            n: {
                arm: getattr(m, measure)
                for arm, m in arms.items()
                if getattr(m, measure) is not None
            }
            for n, arms in by_block.items()
        }
        print(measure)
        for arm in sorted({a for v in values.values() for a in v}):
            cells = " ".join(
                f"{values[n][arm]:.2f}" if arm in values[n] else " n/a" for n in sorted(values)
            )
            line = f"  {arm:<3}{cells}"
            if arm != args.against and any(arm in v and args.against in v for v in values.values()):
                c = contrast(values, arm, args.against, 1)
                line += (
                    f"   minus {args.against}: {c.mean_difference:+.2f} over {c.blocks} blocks, "
                    f"interval {c.interval[0]:+.2f} to {c.interval[1]:+.2f}, p={c.p:.3f}"
                )
                if c.blocks < SMALL:
                    line += " (few blocks: the interval is about the range of the differences)"
            print(line)


if __name__ == "__main__":
    main()
