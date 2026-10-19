"""Model interface and its fake and recorded backends.

A backend turns a request into a response and knows nothing about the log. ``Model``
wraps a backend and records every call as an event with the requested and served model
ids and the routed provider. ``RecordedBackend`` replays those events, which is how audit
replay and counterfactual forks avoid calling a hosted model again.
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from agent_village.eventlog import EventLog, canonical_hash


class ModelError(Exception):
    """A backend could not produce a usable, fully attributed response."""


class NotRecordedError(ModelError):
    """A recorded backend has no response left for this request."""


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class Request:
    model: str
    messages: tuple[Message, ...]
    max_tokens: int
    temperature: float = 0.0

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError("a request needs at least one message")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")

    @property
    def hash(self) -> str:
        return canonical_hash(
            {
                "model": self.model,
                "messages": [[m.role, m.content] for m in self.messages],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        )


@dataclass(frozen=True)
class Response:
    text: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    generation_id: str | None = None
    cost: float | None = None


class Backend(Protocol):
    def complete(self, request: Request) -> Response: ...


class FakeBackend:
    """Deterministic backend for tests and the fake-model village."""

    def __init__(self, reply: Callable[[Request], str] | None = None) -> None:
        self._reply = reply or (lambda request: f"ok {request.hash[:8]}")

    def complete(self, request: Request) -> Response:
        text = self._reply(request)
        prompt_tokens = sum(len(m.content.split()) for m in request.messages)
        return Response(text, request.model, "fake", prompt_tokens, len(text.split()))


class Model:
    def __init__(self, backend: Backend, log: EventLog) -> None:
        self._backend = backend
        self._log = log

    def complete(self, writer: str, request: Request) -> Response:
        response = self._backend.complete(request)
        payload: dict[str, Any] = {
            "request_hash": request.hash,
            "model_requested": request.model,
            "model_served": response.model,
            "provider": response.provider,
            "text": response.text,
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
        }
        if response.generation_id is not None:
            payload["generation_id"] = response.generation_id
        if response.cost is not None:
            payload["cost"] = response.cost
        self._log.append("model_call", writer, payload)
        return response


class RecordedBackend:
    """Replays the responses recorded in a log, per request, in recorded order.

    ``from_log`` can start part way through a log, so a fork replays only the calls made
    after the fork point.
    """

    def __init__(self, responses: dict[str, deque[Response]]) -> None:
        self._responses = responses

    @classmethod
    def from_log(cls, log: EventLog, start: int = 0) -> RecordedBackend:
        if not 0 <= start <= len(log):
            raise ValueError(f"the log has {len(log)} events, not {start}")
        responses: dict[str, deque[Response]] = defaultdict(deque)
        for index in range(start, len(log)):
            event = log[index]
            if event.kind == "model_call":
                p: Any = event.payload
                responses[p["request_hash"]].append(
                    Response(
                        p["text"],
                        p["model_served"],
                        p["provider"],
                        p["prompt_tokens"],
                        p["completion_tokens"],
                        p.get("generation_id"),
                        p.get("cost"),
                    )
                )
        return cls(responses)

    def complete(self, request: Request) -> Response:
        queue = self._responses.get(request.hash)
        if not queue:
            raise NotRecordedError(request.hash)
        return queue.popleft()
