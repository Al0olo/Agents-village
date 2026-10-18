"""Helpers shared by the village tests."""

import random
import re

from agent_village.runner import Spec


def say(to, text):
    return f'{{"action": "say", "to": "{to}", "text": "{text}"}}'


def remember(text, kind="seen", cites=(), tier="core"):
    cited = ", ".join(str(c) for c in cites)
    return (
        f'{{"action": "remember", "text": "{text}", "kind": "{kind}", '
        f'"cites": [{cited}], "tier": "{tier}"}}'
    )


NAMES = ("ada", "bo", "cy", "di", "ed", "flo", "gus", "hal")


def behave(request):
    """A reply fixed by the request content, so a village built from it is deterministic."""
    h = int(request.hash, 16)
    me = request.messages[0].content.split(".")[0].removeprefix("You are ")
    others = [n for n in NAMES if n != me]
    choice = h % 4
    if choice == 0:
        return say(others[(h >> 8) % len(others)], f"news {h % 97}")
    if choice == 1:
        return remember(f"note {h % 89}", "told", [], "shared" if h % 2 else "core")
    return f'{{"action": "sleep", "ticks": {1 + (h >> 4) % 9}}}'


TOLD_LINE = re.compile(r"^\[(\d+)\] (\w+) told you: ", re.MULTILINE)
SAW_LINE = re.compile(r"^\[(\d+)\] You saw: ", re.MULTILINE)


def gossip(request):
    """Chatty citizens that forward what they hear and cite what they saw or were told."""
    h = int(request.hash, 16)
    me = request.messages[0].content.split(".")[0].removeprefix("You are ")
    prompt = request.messages[1].content
    tolds = [(int(i), who) for i, who in TOLD_LINE.findall(prompt)]
    saws = [int(i) for i in SAW_LINE.findall(prompt)]
    others = [n for n in NAMES if n != me]
    choice = h % 6
    if choice == 0:
        return say(others[(h >> 8) % len(others)], f"news {h % 97}")
    if choice == 1 and tolds:
        told, teller = tolds[(h >> 8) % len(tolds)]
        targets = [n for n in others if n != teller]
        return (
            f'{{"action": "forward", "to": "{targets[(h >> 12) % len(targets)]}", "told": {told}}}'
        )
    if choice == 2 and tolds:
        return remember(f"heard {h % 89}", "told", [t for t, _ in tolds], "shared")
    if choice == 3 and saws:
        return remember(f"saw {h % 89}", "seen", saws[:1], "core")
    if choice == 4:
        return remember(f"guess {h % 89}", "seen", [], "shared")
    return f'{{"action": "sleep", "ticks": {1 + (h >> 4) % 3}}}'


def specs():
    return [Spec(n, "fake/model") for n in NAMES]


def observe(world, tick):
    """Environment observations, identical for every arm because they depend only on the tick."""
    rng = random.Random(tick)
    if rng.random() < 0.5:
        who = NAMES[rng.randrange(len(NAMES))]
        world.log.append("saw", who, {"text": f"observation {tick}"})


def drive(world, ticks):
    for _ in range(ticks):
        observe(world, world.village.state().tick + 1)
        world.runner.tick()
