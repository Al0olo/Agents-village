"""A spend cap and a kill switch in front of any backend.

Every live call goes through a ``Gateway``. Before a call it checks the kill file, the call
cap and the cost caps, counting what is already spent plus a reserve for every call in
flight, so threads running arms side by side cannot overshoot a cap by more than the reserve
of a call that was already admitted. After a call it charges the cost the response reports,
or the reserve if the response has none. A refused call raises a ``ModelError`` that is not
transient, so a retry wrapper stops at once; put ``Retrying`` outside the gateway so each
attempt is checked. Once the kill file has been seen the gateway stays stopped.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from agent_village.model import Backend, ModelError, Request, Response


class BudgetExceeded(ModelError):
    """A cost or call cap would be crossed."""


class GatewayStopped(ModelError):
    """The kill switch was thrown."""


class Gateway:
    def __init__(
        self,
        backend: Backend,
        max_cost: float,
        reserve: float,
        max_calls: int | None = None,
        per_model: Mapping[str, float] | None = None,
        kill_file: Path | str | None = None,
    ) -> None:
        if max_cost <= 0 or reserve <= 0 or (max_calls is not None and max_calls < 1):
            raise ValueError("max_cost, reserve and max_calls must be positive")
        if any(cap <= 0 for cap in (per_model or {}).values()):
            raise ValueError("a per-model cap must be positive")
        self._backend = backend
        self._max_cost, self._reserve, self._max_calls = max_cost, reserve, max_calls
        self._per_model = dict(per_model or {})
        self._kill = Path(kill_file) if kill_file else None
        self._lock = threading.Lock()
        self._spent = 0.0
        self._calls = 0
        self._uncosted = 0
        self._by_model: dict[str, float] = defaultdict(float)
        self._reserved = 0.0
        self._reserved_by_model: dict[str, float] = defaultdict(float)
        self._stopped = False

    @property
    def spent(self) -> float:
        return self._spent

    @property
    def calls(self) -> int:
        return self._calls

    @property
    def uncosted(self) -> int:
        return self._uncosted

    @property
    def by_model(self) -> dict[str, float]:
        return dict(self._by_model)

    @property
    def stopped(self) -> bool:
        return self._stopped

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "spent": round(self._spent, 10),
                "calls": self._calls,
                "uncosted": self._uncosted,
                "by_model": {m: round(c, 10) for m, c in self._by_model.items()},
                "stopped": self._stopped,
            }

    def complete(self, request: Request) -> Response:
        model = request.model
        with self._lock:
            self._admit(model)
            self._reserved += self._reserve
            self._reserved_by_model[model] += self._reserve
        try:
            response = self._backend.complete(request)
        except BaseException:
            with self._lock:
                self._release(model)
            raise
        with self._lock:
            self._release(model)
            cost = response.cost
            if cost is None:
                cost = self._reserve
                self._uncosted += 1
            self._spent += cost
            self._by_model[model] += cost
            self._calls += 1
        return response

    def _admit(self, model: str) -> None:
        if self._stopped or (self._kill is not None and self._kill.exists()):
            self._stopped = True
            raise GatewayStopped("the kill switch was thrown")
        if self._max_calls is not None and self._calls >= self._max_calls:
            raise BudgetExceeded(f"the cap of {self._max_calls} calls is reached")
        if self._spent + self._reserved + self._reserve > self._max_cost:
            raise BudgetExceeded(f"the cost cap of {self._max_cost} would be crossed")
        cap = self._per_model.get(model)
        used = self._by_model[model] + self._reserved_by_model[model]
        if cap is not None and used + self._reserve > cap:
            raise BudgetExceeded(f"the cost cap of {cap} for {model} would be crossed")

    def _release(self, model: str) -> None:
        self._reserved -= self._reserve
        self._reserved_by_model[model] -= self._reserve
