import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

import pytest

from agent_village.eventlog import EventLog
from agent_village.model import Message, Model, ModelError, Request, Response
from agent_village.openrouter import (
    OpenRouterBackend,
    Retrying,
    TransientError,
    generation_record,
    served_snapshots,
    urllib_transport,
)


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


def test_the_reasoning_setting_is_sent_per_model_and_only_when_configured():
    plain, off = Script(chat(provider="acme")), Script(chat(provider="acme"))
    OpenRouterBackend(plain).complete(ask())
    settings = {"vendor/model": {"enabled": False}, "other/model": {"effort": "low"}}
    OpenRouterBackend(off, reasoning=settings).complete(ask())
    elsewhere = Script(chat(provider="acme"))
    OpenRouterBackend(elsewhere, reasoning={"other/model": {"enabled": False}}).complete(ask())
    assert "reasoning" not in plain.calls[0][2] and "reasoning" not in elsewhere.calls[0][2]
    assert off.calls[0][2]["reasoning"] == {"enabled": False}


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


def test_the_response_carries_the_generation_id_and_the_real_cost():
    usage = {"prompt_tokens": 4, "completion_tokens": 2, "cost": 1.5e-05}
    response = OpenRouterBackend(Script(chat(provider="acme", usage=usage))).complete(ask())
    assert (response.generation_id, response.cost) == ("gen-1", 1.5e-05)


@pytest.mark.parametrize("cost", [True, "free", None])
def test_a_cost_that_is_not_a_number_is_ignored(cost):
    usage = {"prompt_tokens": 4, "completion_tokens": 2, "cost": cost}
    response = OpenRouterBackend(Script(chat(provider="acme", usage=usage))).complete(ask())
    assert response.cost is None


def test_cost_and_id_are_none_when_the_response_has_none():
    response = OpenRouterBackend(Script(chat(provider="acme", id=None))).complete(ask())
    assert (response.generation_id, response.cost) == (None, None)


@pytest.mark.parametrize("missing", [{}, {"provider": None}, {"provider": ""}, {"provider": 5}])
def test_a_response_that_does_not_name_its_provider_is_an_error(missing):
    with pytest.raises(ModelError):
        OpenRouterBackend(Script(chat(**missing))).complete(ask())


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
        body = Echo.seen[-1][2]
        status, payload = (
            (body.get("status", 500), b"{}") if body.get("fail") else (200, b'{"ok": 1}')
        )
        if body.get("garbage"):
            payload = b"not json"
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


def test_urllib_transport_without_a_key_sends_no_authorization(server, monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    send = urllib_transport(None, base_url=server)
    assert send("POST", "/x", {"a": 1}) == {"ok": 1}
    assert Echo.seen == [("/x", None, {"a": 1})]


def test_urllib_transport_errors_do_not_leak_the_key(server, monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    send = urllib_transport("sk-secret", base_url=server)
    with pytest.raises(ModelError) as info:
        send("POST", "/x", {"fail": True})
    assert "sk-secret" not in str(info.value)


def test_a_failed_request_names_the_http_status(server, monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    send = urllib_transport(None, base_url=server)
    with pytest.raises(ModelError, match="HTTP 500"):
        send("POST", "/x", {"fail": True})


@pytest.mark.parametrize(
    "status,transient", [(429, True), (500, True), (503, True), (400, False), (402, False)]
)
def test_rate_limits_and_server_errors_are_transient_and_other_failures_are_not(
    server, monkeypatch, status, transient
):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    with pytest.raises(ModelError, match=f"HTTP {status}") as info:
        urllib_transport(None, base_url=server)("POST", "/x", {"fail": True, "status": status})
    assert isinstance(info.value, TransientError) is transient


def test_an_unreachable_server_is_transient(server, monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        closed = f"http://127.0.0.1:{sock.getsockname()[1]}"
    with pytest.raises(TransientError):
        urllib_transport(None, base_url=closed)("POST", "/x", {})


def test_an_unreachable_server_or_a_non_json_reply_is_a_model_error(server, monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        closed = f"http://127.0.0.1:{sock.getsockname()[1]}"
    with pytest.raises(ModelError, match="URLError"):
        urllib_transport(None, base_url=closed)("POST", "/x", {})
    with pytest.raises(ModelError, match="JSONDecodeError") as info:
        urllib_transport(None, base_url=server)("POST", "/x", {"garbage": True})
    assert not isinstance(info.value, TransientError)


class Flaky:
    def __init__(self, failures, data):
        self.failures, self.data, self.calls = failures, data, []

    def __call__(self, method, path, body):
        self.calls.append((method, path))
        if self.failures:
            self.failures -= 1
            raise ModelError("not found")
        return {"data": self.data}


def test_the_generation_record_is_polled_until_it_appears():
    sleeps = []
    transport = Flaky(2, {"model": "vendor/model-2026-01-01", "provider_name": "Acme"})
    record = generation_record(transport, "gen-1", attempts=5, delay=3.0, sleep=sleeps.append)
    assert record["model"] == "vendor/model-2026-01-01"
    assert sleeps == [3.0, 3.0]
    assert transport.calls == [("GET", "/generation?id=gen-1")] * 3


def test_the_generation_record_lookup_gives_up_after_its_attempts():
    sleeps = []
    transport = Flaky(99, {})
    with pytest.raises(ModelError):
        generation_record(transport, "gen-1", attempts=3, delay=1.0, sleep=sleeps.append)
    assert len(transport.calls) == 3 and sleeps == [1.0, 1.0]


def test_the_generation_id_is_quoted_in_the_lookup():
    transport = Flaky(0, {"model": "m"})
    generation_record(transport, "gen/1 x", attempts=1, delay=0, sleep=lambda s: None)
    assert transport.calls == [("GET", "/generation?id=gen%2F1%20x")]


def test_a_record_without_data_counts_as_not_ready():
    replies = iter([{"data": None}, {}, {"data": {"model": "m"}}])
    record = generation_record(
        lambda method, path, body: next(replies), "gen-1", attempts=5, delay=0, sleep=lambda s: None
    )
    assert record == {"model": "m"}


def logged(tmp_path, calls):
    log = EventLog(tmp_path / "v.jsonl")
    queue = iter(calls)

    class Scripted:
        def complete(self, request):
            model, gid = next(queue)
            return Response("x", model, "acme", 1, 1, gid)

    for _ in calls:
        Model(Scripted(), log).complete("ada", ask())
    return log


def test_served_snapshots_resolves_a_spread_sample_of_calls_per_requested_model(tmp_path):
    calls = [("vendor/model", f"gen-{n}") for n in range(10)]
    log = logged(tmp_path, calls)
    asked = []

    def transport(method, path, body):
        asked.append(path)
        return {"data": {"model": "vendor/model-2026-01-01"}}

    found = served_snapshots(log, transport, per_model=3, attempts=1, delay=0, sleep=lambda s: None)
    assert found == {"vendor/model": {"vendor/model-2026-01-01"}}
    assert asked == ["/generation?id=gen-0", "/generation?id=gen-4", "/generation?id=gen-9"]


def test_served_snapshots_reports_a_change_and_skips_calls_without_an_id(tmp_path):
    log = logged(tmp_path, [("m", "gen-0"), ("m", None), ("m", "gen-2")])
    snapshots = {"gen-0": "m-2026-01-01", "gen-2": "m-2026-02-01"}

    def transport(method, path, body):
        return {"data": {"model": snapshots[path.split("=")[1]]}}

    found = served_snapshots(log, transport, per_model=5, attempts=1, delay=0, sleep=lambda s: None)
    assert found == {"vendor/model": {"m-2026-01-01", "m-2026-02-01"}}


def test_served_snapshots_of_a_log_with_no_ids_is_empty(tmp_path):
    assert served_snapshots(logged(tmp_path, [("m", None)]), Flaky(0, {})) == {}


class Unreliable:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), 0

    def complete(self, request):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


OK = Response("hi", "vendor/model", "acme", 3, 1)


def test_a_transient_failure_is_retried_after_each_delay_and_the_attempts_are_counted():
    sleeps = []
    backend = Unreliable(TransientError("a"), TransientError("b"), OK)
    got = Retrying(backend, (2.0, 5.0, 10.0), sleeps.append).complete(ask())
    assert (backend.calls, sleeps, got.attempts, got.text) == (3, [2.0, 5.0], 3, "hi")


def test_a_call_that_works_first_time_is_not_delayed_or_counted_as_retried():
    sleeps = []
    got = Retrying(Unreliable(OK), (2.0,), sleeps.append).complete(ask())
    assert (sleeps, got.attempts) == ([], 1)


def test_the_call_gives_up_after_the_last_delay():
    sleeps = []
    backend = Unreliable(*[TransientError("busy")] * 4)
    with pytest.raises(ModelError, match="gave up after 3 attempts: busy") as info:
        Retrying(backend, (1.0, 2.0), sleeps.append).complete(ask())
    assert (backend.calls, sleeps) == (3, [1.0, 2.0])
    assert not isinstance(info.value, TransientError)


def test_a_failure_that_is_not_transient_is_raised_at_once():
    sleeps = []
    backend = Unreliable(ModelError("HTTP 400"), OK)
    with pytest.raises(ModelError, match="HTTP 400"):
        Retrying(backend, (1.0, 2.0), sleeps.append).complete(ask())
    assert (backend.calls, sleeps) == (1, [])


def test_with_no_delays_there_is_one_attempt():
    with pytest.raises(ModelError):
        Retrying(Unreliable(TransientError("x"), OK), ()).complete(ask())


def test_an_answer_with_no_content_says_how_it_ended():
    reply = chat(
        provider="acme", choices=[{"message": {"content": None}, "finish_reason": "length"}]
    )
    with pytest.raises(ModelError, match="no content.*length"):
        OpenRouterBackend(Script(reply)).complete(ask())


def test_a_blank_answer_is_still_an_answer():
    reply = chat(provider="acme", choices=[{"message": {"content": ""}}])
    assert OpenRouterBackend(Script(reply)).complete(ask()).text == ""
