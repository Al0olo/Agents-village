"""Live backend for OpenRouter's OpenAI-compatible chat completions endpoint.

Fallbacks between providers are always off. The routed provider is read from the chat
response when it carries one and otherwise from the generation record; a call whose
provider cannot be determined fails, so no live call is logged without its provider.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from typing import Any

from agent_village.model import ModelError, Request, Response

BASE_URL = "https://openrouter.ai/api/v1"

Transport = Callable[[str, str, Mapping[str, Any] | None], Mapping[str, Any]]


def urllib_transport(api_key: str, base_url: str = BASE_URL, timeout: float = 60.0) -> Transport:
    def send(method: str, path: str, body: Mapping[str, Any] | None) -> Mapping[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        http = urllib.request.Request(
            base_url + path,
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
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
        provider = data.get("provider") or self._routed_provider(data.get("id"))
        return Response(text, served, provider, prompt_tokens, completion_tokens)

    def _routed_provider(self, generation_id: Any) -> str:
        if not isinstance(generation_id, str) or not generation_id:
            raise ModelError("response has no generation id to look the provider up")
        record = self._transport("GET", "/generation?id=" + urllib.parse.quote(generation_id), None)
        name = (record.get("data") or {}).get("provider_name")
        if not isinstance(name, str) or not name:
            raise ModelError("routed provider unknown")
        return name
