"""Message passing with origin tracking.

A send logs a ``message`` event for the sender and a ``told`` event for the recipient
(the evidence ``memory.py`` reads). Origins are the root sources of the information: a
first-hand message has the sender as its only origin, and a forward carries the original
text and adds the forwarder to the origins it received, so origins only ever grow. A
message cannot go to one of its own origins, which also rules out sending to oneself.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_village.eventlog import Log, LogEvent

TOLD_KINDS = ("told", "heard")
"""What a citizen was told: a message from a citizen, or a rumor from a traveler."""


@dataclass(frozen=True)
class Delivery:
    message: int
    told: int


@dataclass(frozen=True)
class Received:
    id: int
    sender: str
    text: str
    origins: frozenset[str]


class Messenger:
    def __init__(self, log: Log) -> None:
        self._log = log

    def send(self, sender: str, recipient: str, text: str) -> Delivery:
        return self._deliver(sender, recipient, text, frozenset({sender}), None)

    def forward(self, forwarder: str, recipient: str, told_id: str) -> Delivery:
        event = self._told_for(forwarder, told_id)
        origins = frozenset(event.payload["origins"]) | {forwarder}
        return self._deliver(forwarder, recipient, event.payload["text"], origins, event.id)

    def received(self, recipient: str, after: int = -1) -> tuple[Received, ...]:
        return tuple(
            Received(e.id, e.payload["from"], e.payload["text"], frozenset(e.payload["origins"]))
            for e in (self._log[i] for i in range(after + 1, len(self._log)))
            if e.kind in TOLD_KINDS and e.writer == recipient
        )

    def _told_for(self, citizen: str, told_id: str) -> LogEvent:
        if not told_id.isdigit() or int(told_id) >= len(self._log):
            raise KeyError(told_id)
        event = self._log[int(told_id)]
        if event.kind not in TOLD_KINDS or event.writer != citizen:
            raise ValueError(f"{told_id} is not a message {citizen} received")
        return event

    def _deliver(
        self,
        sender: str,
        recipient: str,
        text: str,
        origins: frozenset[str],
        forward_of: int | None,
    ) -> Delivery:
        if not sender or not recipient or not text:
            raise ValueError("sender, recipient and text must be non-empty")
        if recipient in origins:
            raise ValueError(f"the message already originates with {recipient}")
        listed = sorted(origins)
        message = self._log.append(
            "message",
            sender,
            {"to": recipient, "text": text, "origins": listed, "forward_of": forward_of},
        )
        told = self._log.append(
            "told",
            recipient,
            {"from": sender, "text": text, "origins": listed, "message": message.id},
        )
        return Delivery(message.id, told.id)
