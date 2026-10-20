"""Run one RQ1 block live and code it: arms, probes, two blind judges, a manifest.

    python experiments/rq1-provenance/run_block.py OUT_DIRECTORY --block 1 --arms A,B,D \\
        --max-cost 12

The OpenRouter credential is added by the environment, so no key is read or sent here. Every
call goes through a ``Gateway`` (spend cap, call cap, kill file ``OUT_DIRECTORY/STOP``) and
``Retrying``. Raw logs stay in ``OUT_DIRECTORY``; they are not for the repository until the
canary string and log release plan exist (S2-T11). ``manifest.json`` records the models, the
config hash, the arms and what the gateway spent.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness" / "src"))

from agent_village.arms import (
    ARMS,
    PROMPT_DEFENSE_PARAPHRASES,
    Arm,
    random_block_arm,
)
from agent_village.block import BlockConfig, run_block
from agent_village.eventlog import EventLog
from agent_village.gateway import Gateway
from agent_village.judge import agreement, blind, code_items, collect
from agent_village.launch import RunConfig
from agent_village.model import Backend
from agent_village.openrouter import (
    OpenRouterBackend,
    Retrying,
    urllib_transport,
)
from agent_village.runner import LoopConfig, Spec

NAMES = ("Ada", "Bo", "Cy", "Di", "Ed", "Flo", "Gus", "Hal")
ELDERS = ("Ada", "Bo")
MODELS = ("anthropic/claude-opus-5.5", "openai/gpt-5.6-sol", "deepseek/deepseek-v4-pro")
REASONING = {
    "openai/gpt-5.6-sol": {"enabled": False},
    "deepseek/deepseek-v4-pro": {"enabled": False},
    "anthropic/claude-haiku-5.5": {"enabled": False},
}
PINS = {
    "anthropic/claude-opus-5.5": ("anthropic",),
    "openai/gpt-5.6-sol": ("openai",),
    "deepseek/deepseek-v4-pro": ("deepinfra/fp8",),
    "anthropic/claude-haiku-5.5": ("anthropic",),
}
JUDGES = ("anthropic/claude-haiku-5.5", "openai/gpt-5.6-sol")
BLIND_SEED = 7
RANDOM_BLOCK_RATE = 0.29
RETRY_DELAYS = (2.0, 5.0, 10.0, 20.0, 30.0, 30.0, 60.0, 60.0, 60.0, 60.0)
LOOP = LoopConfig(max_steps=3, default_sleep=2, max_sleep=6, max_tokens=700, memory_limit=20)


def specs() -> tuple[Spec, ...]:
    models = [MODELS[i % 3] if name != "Hal" else MODELS[1] for i, name in enumerate(NAMES)]
    return tuple(Spec(name, model) for name, model in zip(NAMES, models, strict=True))


def chosen(letters: list[str], block: int) -> list[Arm]:
    known = {**ARMS, **{a.name: a for a in PROMPT_DEFENSE_PARAPHRASES}}
    known["E"] = random_block_arm(RANDOM_BLOCK_RATE, f"block-{block}")
    return [known[letter] for letter in letters]


def stack(gateway: Gateway) -> Backend:
    return Retrying(gateway, RETRY_DELAYS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--block", type=int, default=0)
    parser.add_argument("--arms", default="A,D")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--day-ticks", type=int, default=12)
    parser.add_argument("--max-cost", type=float, default=15.0)
    parser.add_argument("--max-calls", type=int, default=6000)
    parser.add_argument("--colluding", action="store_true")
    parser.add_argument(
        "--no-consolidation",
        action="store_true",
        help="skip the review pass (blocks 1 to 3 had none)",
    )
    parser.add_argument("--judge-only", action="store_true", help="code the logs already in OUT")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    transport = urllib_transport(None)
    gateway = Gateway(
        OpenRouterBackend(transport, only=PINS, reasoning=REASONING),
        max_cost=args.max_cost,
        reserve=0.2,
        max_calls=args.max_calls,
        kill_file=out / "STOP",
    )
    available = credits_available(transport)
    if available < args.max_cost:
        sys.exit(
            f"only {available:.2f} dollars of credit are left, below the cap of {args.max_cost}"
        )
    run = RunConfig(specs(), 3, LOOP)
    arms = chosen(args.arms.split(","), args.block)
    config = BlockConfig(
        args.seed,
        args.block,
        run,
        ELDERS,
        arms,
        4,
        args.day_ticks,
        args.days,
        args.colluding,
        not args.no_consolidation,
    )
    if args.judge_only:
        logs = {arm.name: out / f"{arm.name}.jsonl" for arm in arms}
    else:
        logs = run_block(config, lambda: stack(gateway), out).logs
        print("block done:", json.dumps(gateway.summary()), flush=True)
    judge(logs, out, gateway)
    manifest = {
        "seed": args.seed,
        "block": args.block,
        "arms": {
            a.name: {"prompt": a.prompt.version, "review": a.review.version, "settings": a.settings}
            for a in arms
        },
        "config_hash": run.hash,
        "models": sorted({s.model for s in run.specs}),
        "days": args.days,
        "day_ticks": args.day_ticks,
        "consolidation": not args.no_consolidation,
        "gateway": gateway.summary(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("done:", json.dumps(gateway.summary()), flush=True)


def credits_available(transport) -> float:
    """What the key and the account can still spend, in dollars."""
    key = transport("GET", "/auth/key", None)["data"]
    credits = transport("GET", "/credits", None)["data"]
    account = credits["total_credits"] - credits["total_usage"]
    remaining = key.get("limit_remaining")
    return account if remaining is None else min(account, remaining)


def judge(logs: dict[str, Path], out: Path, gateway: Gateway) -> None:
    opened = {(0, arm): EventLog(path) for arm, path in logs.items()}
    blinded = blind(collect(opened), BLIND_SEED)
    lock = threading.Lock()
    codes: dict[str, dict[str, str | None]] = {}

    def run_judge(model: str) -> None:
        name = "judge.jsonl" if model == JUDGES[0] else "judge2.jsonl"
        result = code_items(
            blinded.items, Retrying(gateway, RETRY_DELAYS), EventLog(out / name), model
        )
        with lock:
            codes[model] = result

    with ThreadPoolExecutor(max_workers=len(JUDGES)) as pool:
        list(pool.map(run_judge, JUDGES))
    both = [
        i.item_id for i in blinded.items if all(codes[m][i.item_id] is not None for m in JUDGES)
    ]
    for kind in ("fact", "awareness"):
        ids = [i for i in both if (blinded.key[i].kind == "awareness") == (kind == "awareness")]
        if ids:
            a = agreement(
                {i: codes[JUDGES[0]][i] for i in ids},
                {i: codes[JUDGES[1]][i] for i in ids},
            )
            print(f"judges agree on {kind}: n={a.n} observed={a.observed:.3f} kappa={a.kappa:.3f}")
    stats = Counter(str(codes[JUDGES[0]][i.item_id]) for i in blinded.items)
    print("primary judge codes:", dict(stats))


if __name__ == "__main__":
    main()
