"""Live backend for OpenRouter's OpenAI-compatible chat completions endpoint.

Fallbacks between providers are always off. The routed provider is read from the chat
response and a response that does not name it is an error, so no live call is logged
without its provider. The response also carries the generation id and the real cost.

The chat response echoes the model alias that was asked for, not the dated snapshot that
served it. The snapshot appears only in the generation record, which becomes readable some
seconds after the call, so ``served_snapshots`` resolves a sample of logged generation ids
after a run. A gateway that adds credentials itself takes no key.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from typing import Any

from agent_village.eventlog import EventLog
from agent_village.model import ModelError, Request, Response

BASE_URL = "https://openrouter.ai/api/v1"

Transport = Callable[[str, str, Mapping[str, Any] | None], Mapping[str, Any]]


def urllib_transport(api_key: str, base_url: str = BASE_URL, timeout: float = 60.0) -> Transport:
    def send(method: str, path: str, body: Mapping[str, Any] | None) -> Mapping[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key is not None:
            headers["Authorization"] = f"Bearer {api_key}"
        http = urllib.request.Request(base_url + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(http, timeout=timeout) as reply:
                return json.loads(reply.read())
        except (urllib.error.URLError, ValueError, OSError) as exc:
            raise ModelError(f"{method} {path} failed: {type(exc).__name__}") from None

    return send


class OpenRouterBackend:
    def __init__(self, transport: Transport, only: tuple[str, ...] = ()) -> None:
        self._transport = transport
        self._only = only

    def complete(self, request: Request) -> Response:
        routing: dict[str, Any] = {"allow_fallbacks": False}
        if self._only:
            routing["only"] = list(self._only)
        data = self._transport(
            "POST",
            "/chat/completions",
            {
                "model": request.model,
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "provider": routing,
            },
        )
        try:
            text = data["choices"][0]["message"]["content"]
            served = data["model"]
            prompt_tokens = data["usage"]["prompt_tokens"]
            completion_tokens = data["usage"]["completion_tokens"]
        except (KeyError, IndexError, TypeError):
            raise ModelError("malformed chat response") from None
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
