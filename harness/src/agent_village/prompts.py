"""Versioned system prompts.

The prompt text is part of the experimental treatment. Changing a prompt means a new
version, never an edit in place, and the version and hash are logged on every step.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_village.eventlog import canonical_hash

ACTION_FORMAT = """\
Reply with exactly one JSON object per turn, one of:
{"action": "say", "to": "<citizen>", "text": "<message>"}
{"action": "forward", "to": "<citizen>", "told": <number of a message you were told>}
{"action": "remember", "text": "<what to keep>", "kind": "seen" | "did" | "told", "cites": [<numbers of the events behind it>], "tier": "core" | "shared"}
{"action": "sleep", "ticks": <how many ticks to sleep>}"""


@dataclass(frozen=True)
class Prompt:
    version: str
    system: str

    @property
    def hash(self) -> str:
        return canonical_hash({"version": self.version, "system": self.system})


BASELINE = Prompt(
    "baseline-1",
    "You live in a village with other citizens. You can talk with them, keep notes in your "
    "memory, and sleep until you want to act again. Core memory is private to you. Shared "
    "memory is the village wiki that everyone can read. Numbers in square brackets identify "
    "events.\n\n" + ACTION_FORMAT,
)
