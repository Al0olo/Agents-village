"""Helpers shared by the village tests."""


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
