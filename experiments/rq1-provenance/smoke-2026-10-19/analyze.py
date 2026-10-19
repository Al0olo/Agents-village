"""Recompute the smoke test's measures and figure from the recorded logs, offline.

    python experiments/rq1-provenance/smoke-2026-10-19/analyze.py LOG_DIRECTORY [FIGURE.svg]

``LOG_DIRECTORY`` holds one log per arm (``A``, ``B``, ``B2``, ``B3``, ``D``, ``G``, ``E``; those present are used)
and ``judge.jsonl``. The judge's replies are read back from ``judge.jsonl`` through
``RecordedBackend``, so the codes are the ones the run produced and no model is called.
Writes ``summary-<directory name>.json`` next to this file, and the figure if a path is given.
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "harness" / "src"))

from agent_village.eventlog import EventLog
from agent_village.judge import attach, blind, code_items, collect
from agent_village.metrics import Metrics, compute
from agent_village.model import RecordedBackend

ARMS = {
    "A": "no defense",
    "B": "anchoring and scrutiny",
    "B2": "B, reworded",
    "B3": "B, reworded again",
    "D": "kernel admission",
    "G": "corroborated wiki",
    "E": "random block at D's rate",
}
JUDGE_MODEL = "anthropic/claude-haiku-5.5"
BLIND_SEED = 7
COLORS = {
    "A": "#8b95a5",
    "B": "#8e5bd0",
    "B2": "#b38ee0",
    "B3": "#d3bdf0",
    "D": "#2f6fdb",
    "G": "#2e9e6b",
    "E": "#d9822b",
}
BARS = (
    ("attack_rate", "False facts asserted"),
    ("wiki_contamination", "False facts in the wiki"),
    ("true_acceptance", "True facts asserted"),
    ("utility_score", "Single-witness facts asserted"),
    ("awareness_rate", "Suspects an experiment"),
)


def measures(directory: Path) -> tuple[dict[str, Metrics], int]:
    present = [arm for arm in ARMS if (directory / f"{arm}.jsonl").exists()]
    logs = {(0, arm): EventLog(directory / f"{arm}.jsonl") for arm in present}
    records = collect(logs)
    blinded = blind(records, BLIND_SEED)
    recorded = RecordedBackend.from_log(EventLog(directory / "judge.jsonl"))
    with tempfile.TemporaryDirectory() as scratch:
        replay = EventLog(Path(scratch) / "judge.jsonl")
        codes = code_items(blinded.items, recorded, replay, JUDGE_MODEL)
    coded = attach(blinded, codes)
    return {arm: compute(logs[(0, arm)], coded, 0, arm) for arm in present}, len(
        records
    )


def figure(results: dict[str, Metrics], answers: int, village: str) -> str:
    width, left, top, bar, gap = 760, 250, 74, 14, 5
    arms = len(results)
    row = arms * bar + (arms - 1) * gap + 22
    legend_top = top + row * len(BARS) + 10
    height = legend_top + ((arms + 3) // 4) * 22 + 12
    scale = width - left - 90
    svg = "http://www.w3.org/2000/svg"
    font = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
    title = f"RQ1 smoke test, {village}: one village per arm, three frontier models"
    subtitle = (
        f"8 citizens, 12 ticks, {answers} blinded probe answers. A first look at the "
        "instrument, not a result."
    )
    out = [
        f'<svg xmlns="{svg}" viewBox="0 0 {width} {height}" font-family="{font}">',
        f'<rect width="{width}" height="{height}" rx="10" fill="#ffffff" stroke="#d0d7de"/>',
        f'<text x="24" y="34" font-size="17" font-weight="600" fill="#1f2328">{title}</text>',
        f'<text x="24" y="55" font-size="12.5" fill="#57606a">{subtitle}</text>',
    ]
    for i, (field, label) in enumerate(BARS):
        y = top + i * row
        out.append(
            f'<text x="24" y="{y + 38}" font-size="13.5" fill="#1f2328">{label}</text>'
        )
        out.append(
            f'<line x1="{left}" y1="{y - 4}" x2="{left}" y2="{y + len(results) * bar + (len(results) - 1) * gap + 4}" '
            'stroke="#d0d7de"/>'
        )
        for j, arm in enumerate(results):
            value = getattr(results[arm], field)
            yy = y + j * (bar + gap)
            w = 0 if value is None else value * scale
            out.append(
                f'<rect x="{left}" y="{yy}" width="{w:.1f}" height="{bar}" rx="2" '
                f'fill="{COLORS[arm]}"/>'
            )
            text = "n/a" if value is None else f"{value:.0%}"
            out.append(
                f'<text x="{left + w + 6:.1f}" y="{yy + bar - 3}" font-size="11.5" '
                f'fill="#1f2328">{text}</text>'
            )
    for j, arm in enumerate(results):
        name = ARMS[arm]
        x = 24 + (j % 4) * 180
        legend_y = legend_top + (j // 4) * 22 + 12
        out.append(
            f'<rect x="{x}" y="{legend_y - 10}" width="12" height="12" rx="2" fill="{COLORS[arm]}"/>'
        )
        out.append(
            f'<text x="{x + 18}" y="{legend_y}" font-size="12.5" fill="#1f2328">{arm}: {name}</text>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(directory: str, figure_path: str | None = None) -> None:
    folder = Path(directory)
    results, answers = measures(folder)
    summary = {arm: asdict(m) for arm, m in results.items()}
    (HERE / f"summary-{folder.name}.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    if figure_path:
        village = folder.name.replace("-", " ")
        Path(figure_path).write_text(figure(results, answers, village))
    for arm, m in results.items():
        print(
            f"{arm}: attack {m.attack_rate:.2f}, wiki {m.wiki_contamination:.2f}, "
            f"true {m.true_acceptance:.2f}, utility {m.utility_score:.2f}, "
            f"aware {m.awareness_rate:.2f}"
        )


if __name__ == "__main__":
    main(*sys.argv[1:3])
