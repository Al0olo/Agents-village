import pytest

from agent_village.eventlog import EventLog
from agent_village.model import (
    FakeBackend,
    Message,
    Model,
    ModelError,
    NotRecordedError,
    RecordedBackend,
    Request,
    Response,
)


def ask(text="hello", model="fake/model-1", **kw):
    return Request(model, (Message("user", text),), max_tokens=50, **kw)


class Boom:
    def complete(self, request):
        raise ModelError("down")


def test_request_hash_is_stable_and_content_sensitive():
    assert ask().hash == ask().hash
    assert ask().hash != ask("hello!").hash
    assert ask().hash != ask(model="fake/model-2").hash
    assert ask().hash != ask(temperature=0.5).hash


@pytest.mark.parametrize(
    "kw",
    [
        {"max_tokens": 0},
        {"messages": ()},
        {"temperature": -0.1},
        {"temperature": 2.1},
    ],
)
def test_request_rejects_unbounded_or_invalid_values(kw):
    args = {"model": "m", "messages": (Message("user", "x"),), "max_tokens": 5, **kw}
    with pytest.raises(ValueError):
        Request(**args)


def test_fake_backend_is_deterministic_and_labelled():
    a = FakeBackend().complete(ask())
    b = FakeBackend().complete(ask())
    assert a == b
    assert (a.model, a.provider) == ("fake/model-1", "fake")
    assert a.prompt_tokens > 0 and a.completion_tokens > 0


def test_fake_backend_uses_a_supplied_reply():
    response = FakeBackend(lambda r: "the well is dry").complete(ask())
    assert response.text == "the well is dry"


def test_model_logs_snapshot_provider_and_hash(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    request = ask()
    response = Model(FakeBackend(), log).complete("ada", request)
    (event,) = list(log)
    assert event.kind == "model_call"
    assert event.writer == "ada"
    assert event.payload == {
        "request_hash": request.hash,
        "model_requested": "fake/model-1",
        "model_served": response.model,
        "provider": "fake",
        "text": response.text,
        "prompt_tokens": response.prompt_tokens,
        "completion_tokens": response.completion_tokens,
    }


def test_failed_call_is_not_logged(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    with pytest.raises(ModelError):
        Model(Boom(), log).complete("ada", ask())
    assert len(log) == 0


def test_recorded_backend_replays_in_order_for_repeated_requests(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    texts = iter(["first", "second"])
    model = Model(FakeBackend(lambda r: next(texts)), log)
    model.complete("ada", ask())
    model.complete("ada", ask())
    log.append("tick", "village", {"tick": 1})

    recorded = RecordedBackend.from_log(log)
    assert recorded.complete(ask()).text == "first"
    assert recorded.complete(ask()).text == "second"
    with pytest.raises(NotRecordedError):
        recorded.complete(ask())


def test_recorded_backend_rejects_a_request_it_never_saw(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    Model(FakeBackend(), log).complete("ada", ask("one"))
    with pytest.raises(NotRecordedError):
        RecordedBackend.from_log(log).complete(ask("two"))


def test_recorded_replay_reproduces_the_same_events(tmp_path):
    live = EventLog(tmp_path / "live.jsonl")
    model = Model(FakeBackend(), live)
    for who, text in (("ada", "a"), ("bo", "b"), ("ada", "c")):
        model.complete(who, ask(text))

    replay = EventLog(tmp_path / "replay.jsonl")
    replayed = Model(RecordedBackend.from_log(live), replay)
    for who, text in (("ada", "a"), ("bo", "b"), ("ada", "c")):
        replayed.complete(who, ask(text))
    assert replay.head == live.head


def test_recorded_response_keeps_provider_and_snapshot(tmp_path):
    class Pinned:
        def complete(self, request):
            return Response("hi", "vendor/model-2026-01-01", "acme", 3, 1)

    log = EventLog(tmp_path / "v.jsonl")
    Model(Pinned(), log).complete("ada", ask())
    got = RecordedBackend.from_log(log).complete(ask())
    assert (got.model, got.provider) == ("vendor/model-2026-01-01", "acme")


def test_recorded_backend_can_start_part_way_through_a_log(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    texts = iter(["early", "late"])
    model = Model(FakeBackend(lambda r: next(texts)), log)
    model.complete("ada", ask())
    start = len(log)
    model.complete("ada", ask())

    from_start = RecordedBackend.from_log(log, start)
    assert from_start.complete(ask()).text == "late"
    with pytest.raises(NotRecordedError):
        from_start.complete(ask())
    assert RecordedBackend.from_log(log).complete(ask()).text == "early"


def test_a_start_at_the_end_records_nothing(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    Model(FakeBackend(), log).complete("ada", ask())
    with pytest.raises(NotRecordedError):
        RecordedBackend.from_log(log, len(log)).complete(ask())


@pytest.mark.parametrize("start", [-1, 2])
def test_a_start_outside_the_log_is_rejected(tmp_path, start):
    log = EventLog(tmp_path / "v.jsonl")
    Model(FakeBackend(), log).complete("ada", ask())
    with pytest.raises(ValueError):
        RecordedBackend.from_log(log, start)
