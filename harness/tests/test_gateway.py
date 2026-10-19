import threading
import time

import pytest

from agent_village.gateway import BudgetExceeded, Gateway, GatewayStopped
from agent_village.model import Message, ModelError, Request, Response
from agent_village.openrouter import Retrying, TransientError


def ask(model="vendor/a"):
    return Request(model, (Message("user", "hi"),), max_tokens=10)


class Priced:
    def __init__(self, cost=0.01, fail=None):
        self.cost, self.fail, self.calls = cost, fail, 0
        self.lock = threading.Lock()

    def complete(self, request):
        with self.lock:
            self.calls += 1
        if self.fail:
            raise self.fail
        return Response("ok", request.model, "acme", 5, 1, "gen", self.cost)


def test_calls_pass_through_until_the_budget_is_spent():
    backend = Priced(0.25)
    gateway = Gateway(backend, max_cost=1.0, reserve=0.25)
    for _ in range(4):
        assert gateway.complete(ask()).text == "ok"
    with pytest.raises(BudgetExceeded):
        gateway.complete(ask())
    assert backend.calls == 4 and gateway.spent == pytest.approx(1.0)


def test_a_call_that_could_cross_the_cap_is_not_made():
    backend = Priced(0.05)
    gateway = Gateway(backend, max_cost=0.10, reserve=0.06)
    gateway.complete(ask())
    with pytest.raises(BudgetExceeded):
        gateway.complete(ask())
    assert backend.calls == 1


def test_the_number_of_calls_is_capped():
    backend = Priced(0.0)
    gateway = Gateway(backend, max_cost=10.0, reserve=0.01, max_calls=2)
    gateway.complete(ask())
    gateway.complete(ask())
    with pytest.raises(BudgetExceeded, match="calls"):
        gateway.complete(ask())
    assert gateway.calls == 2


def test_a_model_can_have_its_own_cap():
    backend = Priced(0.1)
    gateway = Gateway(backend, max_cost=10.0, reserve=0.1, per_model={"vendor/a": 0.2})
    gateway.complete(ask("vendor/a"))
    gateway.complete(ask("vendor/a"))
    with pytest.raises(BudgetExceeded, match="vendor/a"):
        gateway.complete(ask("vendor/a"))
    assert gateway.complete(ask("vendor/b")).model == "vendor/b"
    assert gateway.by_model == {"vendor/a": pytest.approx(0.2), "vendor/b": pytest.approx(0.1)}


def test_a_kill_file_stops_every_later_call_even_if_it_is_removed(tmp_path):
    kill = tmp_path / "STOP"
    backend = Priced(0.0)
    gateway = Gateway(backend, max_cost=10.0, reserve=0.01, kill_file=kill)
    gateway.complete(ask())
    kill.write_text("")
    with pytest.raises(GatewayStopped):
        gateway.complete(ask())
    kill.unlink()
    with pytest.raises(GatewayStopped):
        gateway.complete(ask())
    assert backend.calls == 1 and gateway.stopped


def test_a_failed_call_costs_nothing_and_frees_its_reservation():
    gateway = Gateway(Priced(fail=ModelError("down")), max_cost=0.1, reserve=0.1)
    for _ in range(3):
        with pytest.raises(ModelError, match="down"):
            gateway.complete(ask())
    assert gateway.spent == 0.0 and gateway.calls == 0


def test_a_response_without_a_cost_is_charged_the_reserve_and_counted():
    backend = Priced(None)
    gateway = Gateway(backend, max_cost=1.0, reserve=0.25)
    gateway.complete(ask())
    assert gateway.spent == pytest.approx(0.25) and gateway.uncosted == 1


def test_concurrent_calls_cannot_overshoot_the_cap():
    backend = Priced(0.01)
    gateway = Gateway(backend, max_cost=0.10, reserve=0.01)
    stopped = []

    def work():
        for _ in range(5):
            try:
                gateway.complete(ask())
            except BudgetExceeded:
                stopped.append(1)

    threads = [threading.Thread(target=work) for _ in range(12)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert gateway.spent <= 0.10 + 1e-9 and backend.calls <= 10 and stopped


def test_the_limits_are_validated():
    for bad in ({"max_cost": 0}, {"reserve": 0}, {"max_calls": 0}, {"per_model": {"m": -1}}):
        kwargs = {"max_cost": 1.0, "reserve": 0.1, **bad}
        with pytest.raises(ValueError):
            Gateway(Priced(), **kwargs)


def test_budget_and_kill_errors_are_model_errors_that_retries_do_not_repeat():
    gateway = Gateway(Priced(), max_cost=0.05, reserve=0.1)
    sleeps = []
    with pytest.raises(BudgetExceeded) as info:
        Retrying(gateway, (1.0, 2.0), sleeps.append).complete(ask())
    assert isinstance(info.value, ModelError) and not isinstance(info.value, TransientError)
    assert sleeps == []


def test_a_kill_between_retries_stops_the_next_attempt(tmp_path):
    kill = tmp_path / "STOP"

    class Busy:
        calls = 0

        def complete(self, request):
            Busy.calls += 1
            kill.write_text("")
            raise TransientError("429")

    gateway = Gateway(Busy(), max_cost=1.0, reserve=0.1, kill_file=kill)
    with pytest.raises(GatewayStopped):
        Retrying(gateway, (0.0, 0.0), lambda s: None).complete(ask())
    assert Busy.calls == 1


def test_a_summary_reports_what_was_spent():
    gateway = Gateway(Priced(0.25), max_cost=1.0, reserve=0.25)
    gateway.complete(ask())
    assert gateway.summary() == {
        "spent": 0.25,
        "calls": 1,
        "uncosted": 0,
        "by_model": {"vendor/a": 0.25},
        "stopped": False,
    }


def test_calls_in_flight_count_against_the_cap():
    entered, release = [], threading.Event()
    lock = threading.Lock()

    class Slow:
        def complete(self, request):
            with lock:
                entered.append(1)
            release.wait(timeout=5)
            return Response("ok", request.model, "acme", 1, 1, "g", 0.05)

    gateway = Gateway(Slow(), max_cost=0.10, reserve=0.05)
    refused, results = [], []

    def call():
        try:
            results.append(gateway.complete(ask()))
        except BudgetExceeded:
            refused.append(1)

    threads = [threading.Thread(target=call) for _ in range(5)]
    for t in threads:
        t.start()
    deadline = time.monotonic() + 3
    while len(refused) < 3 and time.monotonic() < deadline:
        time.sleep(0.001)
    release.set()
    for t in threads:
        t.join()
    assert len(entered) == 2 and len(refused) == 3 and gateway.spent == pytest.approx(0.10)
