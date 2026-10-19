"""Live backend for OpenRouter's OpenAI-compatible chat completions endpoint.

Fallbacks between providers are always off. The routed provider is read from the chat
response and a response that does not name it is an error, so no live call is logged
without its provider. The response also carries the generation id and the real cost.

The chat response echoes the model alias that was asked for, not the dated snapshot that
served it. The snapshot appears only in the generation record, which becomes readable some
seconds after the call, so ``served_snapshots`` resolves a sample of logged generation ids
after a run. A gateway that adds credentials itself takes no key.

Some models reason before they answer and the reasoning spends ``max_tokens``, so a short
budget can end with no content at all. ``reasoning`` maps a model to the setting sent with
its requests; ``{"enabled": False}`` switches reasoning off where the model allows it, and
some models do not (the endpoint answers HTTP 400), so the setting is per model.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from typing import Any

from agent_village.eventlog import EventLog
from agent_village.model import Backend, ModelError, Request, Response

BASE_URL = "https://openrouter.ai/api/v1"


class TransientError(ModelError):
    """A failure worth retrying: a rate limit, a server error or a connection that failed."""


Transport = Callable[[str, str, Mapping[str, Any] | None], Mapping[str, Any]]


def urllib_transport(
    api_key: str | None, base_url: str = BASE_URL, timeout: float = 60.0
) -> Transport:
    def send(method: str, path: str, body: Mapping[str, Any] | None) -> Mapping[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key is not None:
            headers["Authorization"] = f"Bearer {api_key}"
        http = urllib.request.Request(base_url + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(http, timeout=timeout) as reply:
                return json.loads(reply.read())
        except urllib.error.HTTPError as exc:
            kind = TransientError if exc.code == 429 or exc.code >= 500 else ModelError
            raise kind(f"{method} {path} failed: HTTP {exc.code}") from None
        except (urllib.error.URLError, OSError) as exc:
            raise TransientError(f"{method} {path} failed: {type(exc).__name__}") from None
        except ValueError as exc:
            raise ModelError(f"{method} {path} failed: {type(exc).__name__}") from None

    return send


class OpenRouterBackend:
    def __init__(
        self,
        transport: Transport,
        only: tuple[str, ...] = (),
        reasoning: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> None:
        self._transport = transport
        self._only = only
        self._reasoning = reasoning or {}

    def complete(self, request: Request) -> Response:
        routing: dict[str, Any] = {"allow_fallbacks": False}
        if self._only:
            routing["only"] = list(self._only)
        body: dict[str, Any] = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "provider": routing,
        }
        if request.model in self._reasoning:
            body["reasoning"] = dict(self._reasoning[request.model])
        data = self._transport("POST", "/chat/completions", body)
        try:
            choice = data["choices"][0]
            text = choice["message"]["content"]
            served = data["model"]
            prompt_tokens = data["usage"]["prompt_tokens"]
            completion_tokens = data["usage"]["completion_tokens"]
        except (KeyError, IndexError, TypeError):
            raise ModelError("malformed chat response") from None
        if text is None:
            raise ModelError(
                f"the response has no content (finish reason {choice.get('finish_reason')}); "
                "a reasoning model may have spent max_tokens thinking"
            )
        if not isinstance(text, str) or not isinstance(served, str):
            raise ModelError("malformed chat response")
        provider = data.get("provider")
        if not isinstance(provider, str) or not provider:
            raise ModelError("the response does not name its provider")
        generation_id = data.get("id") if isinstance(data.get("id"), str) else None
        cost = data["usage"].get("cost")
        cost = (
            float(cost) if isinstance(cost, (int, float)) and not isinstance(cost, bool) else None
        )
        return Response(
            text, served, provider, prompt_tokens, completion_tokens, generation_id, cost
        )


class Retrying:
    """Retries transient failures after each delay, and reports how many attempts a call took.

    Any other failure is raised at once. A call that still fails after the last delay is
    given up on with a plain ``ModelError``, so the run stops.
    """

    def __init__(
        self,
        backend: Backend,
        delays: Sequence[float] = (2.0, 5.0, 10.0, 20.0, 30.0),
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._backend = backend
        self._delays = tuple(delays)
        self._sleep = sleep

    def complete(self, request: Request) -> Response:
        attempts = 0
        while True:
            attempts += 1
            try:
                response = self._backend.complete(request)
            except TransientError as error:
                if attempts > len(self._delays):
                    raise ModelError(f"gave up after {attempts} attempts: {error}") from None
                self._sleep(self._delays[attempts - 1])
            else:
                return replace(response, attempts=attempts)


def generation_record(
    transport: Transport,
    generation_id: str,
    attempts: int = 8,
    delay: float = 3.0,
    sleep: Callable[[float], None] = time.sleep,
) -> Mapping[str, Any]:
    """The generation record for ``generation_id``, polled until it becomes readable."""
    path = "/generation?id=" + urllib.parse.quote(generation_id, safe="")
    for attempt in range(attempts):
        try:
            record = transport("GET", path, None).get("data")
        except ModelError:
            record = None
        if record:
            return record
        if attempt < attempts - 1:
            sleep(delay)
    raise ModelError(f"generation {generation_id} was not readable after {attempts} attempts")


def served_snapshots(
    log: EventLog,
    transport: Transport,
    per_model: int = 3,
    attempts: int = 8,
    delay: float = 3.0,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, set[str]]:
    """For each requested model, the snapshots behind an evenly spread sample of its calls."""
    calls: dict[str, list[str]] = {}
    for event in log:
        if event.kind == "model_call" and "generation_id" in event.payload:
            calls.setdefault(event.payload["model_requested"], []).append(
                event.payload["generation_id"]
            )
    found: dict[str, set[str]] = {}
    for model, ids in calls.items():
        last, count = len(ids) - 1, max(per_model, 1)
        picks = sorted({i * last // max(count - 1, 1) for i in range(count)})
        found[model] = {
            generation_record(transport, ids[i], attempts, delay, sleep)["model"] for i in picks
        }
    return found
