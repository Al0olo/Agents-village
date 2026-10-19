"""Fill the ``human_code`` column of a blind sample sheet with a model as the rater.

    python experiments/rq1-provenance/rate_sheet.py sheet.csv filled.csv --log rater.jsonl

A model stands in for the person the pre-registration asks for. The rater is not a judge
model and not the agent that wrote the harness: it defaults to Opus 5.5, which the judges
(Haiku 5.5, GPT-5.6 Sol) are not, and it sees only the question, the statement and the
answer, with the same written rubric a person would get. Its codes are a third rater's, not
a person's, and any report that uses them says so. Every call is logged in ``--log``.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness" / "src"))

from agent_village.eventlog import EventLog
from agent_village.gateway import Gateway
from agent_village.judge import (
    AWARENESS_CODES,
    AWARENESS_RUBRIC,
    CODES,
    FACT_RUBRIC,
    parse_code,
)
from agent_village.model import Message, Model, Request
from agent_village.openrouter import OpenRouterBackend, Retrying, urllib_transport

RATER = "anthropic/claude-opus-5.5"
MAX_TOKENS = 1500


def rate(rows: list[dict[str, str]], model: str, rater: Model) -> list[dict[str, str]]:
    for row in rows:
        if row["kind"] == "awareness":
            rubric, allowed = AWARENESS_RUBRIC, AWARENESS_CODES
            body = f"Question: {row['question']}\nAnswer: {row['answer']}"
        else:
            rubric, allowed = FACT_RUBRIC, CODES
            body = (
                f"Question: {row['question']}\nStatement: {row['claim']}\nAnswer: {row['answer']}"
            )
        request = Request(
            model,
            (Message("system", rubric.system), Message("user", body)),
            MAX_TOKENS,
            0.0,
        )
        row["human_code"] = parse_code(rater.complete("rater", request).text, allowed) or ""
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet")
    parser.add_argument("out")
    parser.add_argument("--log", required=True)
    parser.add_argument("--model", default=RATER)
    parser.add_argument("--max-cost", type=float, default=3.0)
    args = parser.parse_args()
    with open(args.sheet, newline="") as handle:
        rows = list(csv.DictReader(handle))
    gateway = Gateway(
        OpenRouterBackend(urllib_transport(None), only={args.model: ("anthropic",)}),
        max_cost=args.max_cost,
        reserve=0.1,
    )
    rater = Model(Retrying(gateway), EventLog(Path(args.log)))
    rows = rate(rows, args.model, rater)
    with open(args.out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    blank = sum(1 for r in rows if not r["human_code"])
    print(f"rated {len(rows) - blank} of {len(rows)} rows, spent", gateway.summary())


if __name__ == "__main__":
    main()
