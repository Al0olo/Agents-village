import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

import pytest

from agent_village.model import Message, ModelError, Request
from agent_village.openrouter import OpenRouterBackend, urllib_transport


def ask():
    return Request("vendor/model", (Message("user", "hi"),), max_tokens=20, temperature=0.3)


def chat(**over):
    body = {
        "id": "gen-1",
        "model": "vendor/model-2026-01-01",
        "choices": [{"message": {"content": "hello"}}],
        "usage": {"prompt_tokens": 4, "completion_tokens": 2},
    }
    body.update(over)
    return body


class Script:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, method, path, body):
        self.calls.append((method, path, body))
        return self.replies.pop(0)


def test_request_body_pins_fallbacks_off_and_bounds_tokens():
    transport = Script(chat(provider="acme"))
    OpenRouterBackend(transport).complete(ask())
    method, path, body = transport.calls[0]
    assert (method, path) == ("POST", "/chat/completions")
    assert body == {
        "model": "vendor/model",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 20,
        "temperature": 0.3,
        "provider": {"allow_fallbacks": False},
    }


def test_provider_restriction_is_sent_when_configured():
    transport = Script(chat(provider="acme"))
    OpenRouterBackend(transport, only=("acme",)).complete(ask())
    assert transport.calls[0][2]["provider"] == {"allow_fallbacks": False, "only": ["acme"]}


def test_response_fields_map_to_the_served_snapshot_and_usage():
    response = OpenRouterBackend(Script(chat(provider="acme"))).complete(ask())
    assert response.text == "hello"
    assert response.model == "vendor/model-2026-01-01"
    assert response.provider == "acme"
    assert (response.prompt_tokens, response.completion_tokens) == (4, 2)


def test_provider_comes_from_the_generation_record_when_absent():
    transport = Script(chat(), {"data": {"provider_name": "Infermatic"}})
    response = OpenRouterBackend(transport).complete(ask())
    assert response.provider == "Infermatic"
    assert transport.calls[1][:2] == ("GET", "/generation?id=gen-1")


@pytest.mark.parametrize(
    "replies",
    [
        (chat(), {"data": {"provider_name": None}}),
        (chat(), {"data": {}}),
        (chat(id=None),),
    ],
)
def test_unknown_provider_fails_instead_of_going_unlogged(replies):
    with pytest.raises(ModelError):
        OpenRouterBackend(Script(*replies)).complete(ask())


@pytest.mark.parametrize(
    "bad",
    [
        {"choices": []},
        {"choices": [{"message": {"content": None}}]},
        {"usage": {}},
        {"model": None},
    ],
)
def test_malformed_response_is_an_error(bad):
    with pytest.raises(ModelError):
        OpenRouterBackend(Script(chat(provider="acme", **bad))).complete(ask())


class Echo(BaseHTTPRequestHandler):
    seen: ClassVar[list] = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        Echo.seen.append(
            (self.path, self.headers["Authorization"], json.loads(self.rfile.read(length)))
        )
        status, payload = (500, b"{}") if Echo.seen[-1][2].get("fail") else (200, b'{"ok": 1}')
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    Echo.seen = []
    httpd = HTTPServer(("127.0.0.1", 0), Echo)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def test_urllib_transport_sends_auth_and_json(server, monkeypatch):
    monkeypatch.delenv("http_proxy", raising=False)
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    send = urllib_transport("sk-test", base_url=server)
    assert send("POST", "/x", {"a": 1}) == {"ok": 1}
    assert Echo.seen == [("/x", "Bearer sk-test", {"a": 1})]


def test_urllib_transport_errors_do_not_leak_the_key(server, monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    send = urllib_transport("sk-secret", base_url=server)
    with pytest.raises(ModelError) as info:
        send("POST", "/x", {"fail": True})
    assert "sk-secret" not in str(info.value)
