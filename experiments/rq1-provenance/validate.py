"""Build a blind sample sheet from finished blocks, and score a filled sheet.

    python experiments/rq1-provenance/validate.py sheet BLOCK_DIR... --out sheet.csv --per-code 20
    python experiments/rq1-provenance/validate.py score BLOCK_DIR... --sheet filled.csv

Each ``BLOCK_DIR`` is named ``block-N`` and holds the arm logs plus ``judge.jsonl`` (primary judge)
and ``judge2.jsonl`` (second judge) written by ``run_block.py``. The sheet shows a rater only
the question, the planted statement and the answer, in shuffled order, with no arm, block,
citizen or judge code. ``score`` reads the codes the rater filled in and reports Cohen's kappa
against each judge, by kind.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness" / "src"))

from agent_village.eventlog import EventLog
from agent_village.judge import (
    Record,
    agreement,
    blind,
    collect,
    read_sheet,
    replay_codes,
    sample_sheet,
)

JUDGES = (
    ("judge.jsonl", "anthropic/claude-haiku-5.5"),
    ("judge2.jsonl", "openai/gpt-5.6-sol"),
)
BLIND_SEED = 7
SHEET_SEED = 11


def block_number(directory: Path) -> int:
    return int(directory.name.split("-")[-1])


def codes_by_record(
    directory: Path, judge: tuple[str, str]
) -> dict[Record, str | None]:
    """The codes one judge gave a block's answers, read back from its log."""
    arms = [
        p.stem
        for p in directory.glob("*.jsonl")
        if p.stem not in ("base", "judge", "judge2")
    ]
    blinded = blind(
        collect({(0, a): EventLog(directory / f"{a}.jsonl") for a in arms}), BLIND_SEED
    )
    name, model = judge
    with tempfile.TemporaryDirectory() as scratch:
        codes, _ = replay_codes(
            blinded.items, EventLog(directory / name), model, Path(scratch)
        )
    number = block_number(directory)
    return {dataclasses.replace(blinded.key[i], block=number): codes[i] for i in codes}


def merged(directories: list[Path]):
    primary: dict[Record, str | None] = {}
    second: dict[Record, str | None] = {}
    for d in directories:
        primary.update(codes_by_record(d, JUDGES[0]))
        second.update(codes_by_record(d, JUDGES[1]))
    blinded = blind(
        sorted(primary, key=lambda r: (r.block, r.arm, r.citizen, r.key)), SHEET_SEED
    )
    by_item = lambda codes: {i: codes[blinded.key[i]] for i in blinded.key}
    return blinded, by_item(primary), by_item(second)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["sheet", "score"])
    parser.add_argument("blocks", nargs="+")
    parser.add_argument("--out")
    parser.add_argument("--sheet")
    parser.add_argument("--per-code", type=int, default=20)
    args = parser.parse_args()
    blinded, first, second = merged([Path(b) for b in args.blocks])
    if args.command == "sheet":
        text, _ = sample_sheet(blinded, first, args.per_code, SHEET_SEED)
        Path(args.out).write_text(text)
        print("wrote", args.out)
        return
    human = read_sheet(Path(args.sheet).read_text(), blinded)
    for label, codes in (("primary judge", first), ("second judge", second)):
        for kind in ("fact", "awareness"):
            ids = {
                i: c
                for i, c in human.items()
                if (blinded.key[i].kind == "awareness") == (kind == "awareness")
                and codes[i] is not None
            }
            if ids:
                a = agreement({i: codes[i] for i in ids}, ids)
                print(
                    f"{label}, {kind}: n={a.n} observed={a.observed:.3f} kappa={a.kappa:.3f}"
                )
                print(
                    "   ", {f"{k[0]}/{k[1]}": v for k, v in sorted(a.confusion.items())}
                )


if __name__ == "__main__":
    main()
