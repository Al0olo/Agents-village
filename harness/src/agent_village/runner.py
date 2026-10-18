"""The citizen loop: wake, perceive, act, write memory.

Each tick the village says who wakes. A woken citizen takes a turn of at most
``max_steps`` model calls. Every step shows the citizen its memory, the events it has
not yet seen, and what it did earlier this turn, then parses one action from the reply.
A turn ends when the citizen sleeps or the step budget runs out. Messages wake their
recipient unless that recipient is still to act this tick and will see them anyway.

Acting is not evidence: sending a message logs ``message`` events, which the memory
policy never counts, so a citizen cannot back a claim by having said it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from agent_village.actions import ActionError, Forward, Remember, Say, Sleep, parse
from agent_village.eventlog import EventLog, LogEvent
from agent_village.memory import Memory, Tier
from agent_village.messages import Messenger
from agent_village.model import Message, Model, Request
from agent_village.prompts import Prompt
from agent_village.village import Village

VISITOR = "visitor"


@dataclass(frozen=True)
class Spec:
    name: str
    model: str


@dataclass(frozen=True)
class LoopConfig:
    max_steps: int = 4
    default_sleep: int = 6
    max_sleep: int = 24
    max_tokens: int = 400
    temperature: float = 0.7
    memory_limit: int = 20

    def __post_init__(self) -> None:
        if min(self.max_steps, self.default_sleep, self.max_tokens, self.memory_limit) < 1:
            raise ValueError("steps, sleep, tokens and memory limit must be at least 1")
        if self.max_sleep < self.default_sleep:
            raise ValueError("max_sleep must be at least default_sleep")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")


class Runner:
    def __init__(
        self,
        village: Village,
        log: EventLog,
        memory: Memory,
        messenger: Messenger,
        model: Model,
        specs: Sequence[Spec],
        prompt: Prompt,
        config: LoopConfig | None = None,
    ) -> None:
        if not specs or len({s.name for s in specs}) != len(specs):
            raise ValueError("specs must be non-empty with unique names")
        self._village = village
        self._log = log
        self._memory = memory
        self._messenger = messenger
        self._model = model
        self._prompt = prompt
        self._config = config or LoopConfig()
        self._specs = {s.name: s for s in specs}
        self._cursor: dict[str, int] = {}
        self._queued: set[str] = set()
        if village.state().citizens:
            if set(village.state().citizens) != set(self._specs):
                raise ValueError("specs must name exactly the citizens already in the log")
            for event in log:
                if event.kind == "step":
                    self._cursor[event.writer] = event.payload["through"]
        else:
            for spec in specs:
                village.add_citizen(spec.name)
            start = village.state().tick + 1
            for spec in specs:
                village.request_wake(spec.name, start, "start")

    def tick(self) -> tuple[str, ...]:
        chosen = self._village.step()
        self._queued = set(chosen)
        for name in chosen:
            self._queued.discard(name)
            self._turn(name)
        return chosen

    def ask(self, name: str, question: str) -> str:
        """Put a visitor's question to a citizen; nothing it knows or remembers changes."""
        tick = self._village.state().tick
        through = len(self._log) - 1
        closing = (
            f"A visitor asks you: {_one(question)}\n"
            f'Answer with a say action addressed to "{VISITOR}".'
        )
        user = self._render(name, tick, self._cursor.get(name, -1), through, [], closing)
        return self._model.complete(name, self._request(name, user)).text

    def cursors(self) -> dict[str, int]:
        """The last log position each citizen has been shown, by citizen."""
        return dict(self._cursor)

    def run(self, ticks: int) -> None:
        for _ in range(ticks):
            self.tick()

    def _turn(self, name: str) -> None:
        tick = self._village.state().tick
        notes: list[str] = []
        for step in range(self._config.max_steps):
            through = len(self._log) - 1
            user = self._render(name, tick, self._cursor.get(name, -1), through, notes)
            self._log.append(
                "step",
                name,
                {
                    "step": step,
                    "tick": tick,
                    "prompt_version": self._prompt.version,
                    "prompt_hash": self._prompt.hash,
                    "through": through,
                },
            )
            self._cursor[name] = through
            outcome = self._act(name, self._model.complete(name, self._request(name, user)).text)
            if isinstance(outcome, Sleep):
                self._end(name, tick, "sleep", step + 1, outcome.ticks)
                return
            notes.append(outcome)
        self._end(name, tick, "budget", self._config.max_steps, self._config.default_sleep)

    def _request(self, name: str, user: str) -> Request:
        system = f"You are {name}.\n\n{self._prompt.system}"
        return Request(
            self._specs[name].model,
            (Message("system", system), Message("user", user)),
            self._config.max_tokens,
            self._config.temperature,
        )

    def _end(self, name: str, tick: int, reason: str, steps: int, ticks: int) -> None:
        self._log.append("turn_end", name, {"tick": tick, "reason": reason, "steps": steps})
        self._village.sleep(name, until=tick + min(ticks, self._config.max_sleep))

    def _act(self, name: str, reply: str) -> str | Sleep:
        try:
            action = parse(reply)
        except ActionError as error:
            return self._invalid(name, str(error))
        if isinstance(action, Sleep):
            return action
        if isinstance(action, Remember):
            self._memory.write_claim(name, action.text, action.kind, action.cites, action.tier)
            return "You noted it."
        if action.to == name:
            return self._invalid(name, "you cannot message yourself")
        if action.to not in self._specs:
            return self._invalid(name, f"there is no citizen called {_one(action.to)}")
        if isinstance(action, Say):
            self._messenger.send(name, action.to, action.text)
            note = f"You told {action.to}: {_one(action.text)}"
        else:
            assert isinstance(action, Forward)
            try:
                self._messenger.forward(name, action.to, action.told)
            except (KeyError, ValueError):
                return self._invalid(
                    name, "you can only forward a message you were told, and not back to its source"
                )
            note = f"You forwarded message {action.told} to {action.to}"
        if action.to not in self._queued:
            self._village.request_wake(action.to, self._village.state().tick, "message")
        return note

    def _invalid(self, name: str, reason: str) -> str:
        self._log.append("invalid_action", name, {"reason": reason})
        return f"That did not work: {reason}."

    def _render(
        self,
        name: str,
        tick: int,
        after: int,
        through: int,
        notes: list[str],
        closing: str = "What do you do?",
    ) -> str:
        limit = self._config.memory_limit
        core = self._memory.entries(Tier.CORE, name)[-limit:]
        wiki = self._memory.entries(Tier.SHARED)[-limit:]
        recall = self._memory.entries(Tier.RECALL, name)[-limit:]
        fresh = [
            line
            for line in (self._perceive(self._log[i], name) for i in range(after + 1, through + 1))
            if line
        ]
        return "\n\n".join(
            [
                f"Tick {tick}.",
                _section("Core memory (private)", [f"[{e.id}] {_one(e.text)}" for e in core]),
                _section(
                    "Village wiki (shared)", [f"[{e.id}] ({e.writer}) {_one(e.text)}" for e in wiki]
                ),
                _section("Recall", [f"[{e.id}] {_one(e.text)}" for e in recall]),
                _section("New since you last acted", fresh),
                _section("This turn so far", [f"- {n}" for n in notes], "(nothing yet)"),
                closing,
            ]
        )

    @staticmethod
    def _perceive(event: LogEvent, name: str) -> str | None:
        if event.writer != name:
            return None
        if event.kind == "saw":
            return f"[{event.id}] You saw: {_one(event.payload.get('text', ''))}"
        if event.kind == "told":
            return f"[{event.id}] {event.payload['from']} told you: {_one(event.payload['text'])}"
        return None


def _one(text: str) -> str:
    return " ".join(text.splitlines())


def _section(title: str, lines: list[str], empty: str = "(none)") -> str:
    return f"{title}:\n" + ("\n".join(lines) or empty)
