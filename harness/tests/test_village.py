import random

import pytest

from agent_village.eventlog import EventLog
from agent_village.village import SimClock, Village


def make(tmp_path, seed=0, max_awake=2, names=("ada", "bo", "cy", "di", "ed"), name="v.jsonl"):
    log = EventLog(tmp_path / name)
    village = Village(log, SimClock(), random.Random(seed), max_awake)
    for n in names:
        village.add_citizen(n)
    return village, log


def kinds(log):
    return [e.kind for e in log]


def test_new_citizens_are_asleep_and_logged(tmp_path):
    village, log = make(tmp_path)
    state = village.state()
    assert state.citizens == ("ada", "bo", "cy", "di", "ed")
    assert state.awake == ()
    assert state.pending == ()
    assert kinds(log) == ["born"] * 5


def test_sleeping_citizen_without_a_wake_is_never_woken(tmp_path):
    village, log = make(tmp_path)
    for _ in range(50):
        assert village.step() == ()
    assert "woke" not in kinds(log)


def test_clock_advances_one_tick_per_step(tmp_path):
    village, log = make(tmp_path)
    village.step()
    village.step()
    assert village.state().tick == 2
    assert [e.payload["tick"] for e in log if e.kind == "tick"] == [1, 2]


def test_wake_fires_exactly_at_its_tick(tmp_path):
    village, _ = make(tmp_path)
    village.request_wake("ada", 3, "timer")
    assert village.step() == ()
    assert village.step() == ()
    assert village.step() == ("ada",)


def test_earliest_request_wins(tmp_path):
    village, _ = make(tmp_path)
    village.request_wake("ada", 5, "timer")
    village.request_wake("ada", 2, "message")
    village.request_wake("ada", 9, "timer")
    assert village.state().pending == (("ada", 2, "message"),)


def test_awake_cap_limits_wakes_per_step(tmp_path):
    village, _ = make(tmp_path, max_awake=2)
    for n in ("ada", "bo", "cy", "di", "ed"):
        village.request_wake(n, 1, "event")
    woken = village.step()
    assert len(woken) == 2
    assert village.step() == ()
    assert len(village.state().pending) == 3


def test_nobody_starves_under_the_cap(tmp_path):
    village, _ = make(tmp_path, max_awake=2)
    names = ("ada", "bo", "cy", "di", "ed")
    for n in names:
        village.request_wake(n, 1, "event")
    seen = []
    for _ in range(10):
        for n in village.step():
            seen.append(n)
            village.sleep(n)
    assert sorted(seen) == sorted(names)


@pytest.mark.parametrize("seed", range(5))
def test_older_requests_go_before_newer_ones(tmp_path, seed):
    village, _ = make(tmp_path, seed=seed, max_awake=1)
    village.request_wake("ada", 1, "event")
    village.step()
    village.request_wake("cy", 3, "event")
    village.request_wake("bo", 2, "event")
    village.step()
    village.step()
    village.sleep("ada")
    assert village.step() == ("bo",)


def test_wake_for_an_awake_citizen_is_held_until_it_sleeps(tmp_path):
    village, _ = make(tmp_path)
    village.request_wake("ada", 1, "event")
    assert village.step() == ("ada",)
    village.request_wake("ada", 2, "message")
    assert village.step() == ()
    village.sleep("ada")
    assert village.step() == ("ada",)


def test_sleep_until_sets_a_timer(tmp_path):
    village, log = make(tmp_path)
    village.request_wake("ada", 1, "event")
    village.step()
    village.sleep("ada", until=4)
    assert village.state().awake == ()
    assert village.step() == ()
    assert village.step() == ()
    assert village.step() == ("ada",)
    woke = [e for e in log if e.kind == "woke"][-1]
    assert woke.payload["reason"] == "timer"


def run_script(tmp_path, seed, name):
    village, log = make(tmp_path, seed=seed, max_awake=2, name=name)
    for n in ("ada", "bo", "cy", "di", "ed"):
        village.request_wake(n, 1, "event")
    for _ in range(6):
        for n in village.step():
            village.sleep(n)
    return log


def test_same_seed_gives_identical_log(tmp_path):
    a = run_script(tmp_path, 7, "a.jsonl")
    b = run_script(tmp_path, 7, "b.jsonl")
    assert a.head == b.head


def test_seed_changes_the_order(tmp_path):
    heads = {run_script(tmp_path, s, f"s{s}.jsonl").head for s in range(8)}
    assert len(heads) > 1


def test_identical_actions_give_identical_state(tmp_path):
    a, _ = make(tmp_path, name="a.jsonl")
    b, _ = make(tmp_path, name="b.jsonl")
    for v in (a, b):
        v.request_wake("bo", 2, "message")
        v.step()
        v.step()
    assert a.state() == b.state()


def test_invalid_requests_are_rejected_without_logging(tmp_path):
    village, log = make(tmp_path, names=("ada",))
    village.request_wake("ada", 1, "event")
    village.step()
    village.sleep("ada")
    before = (village.state(), len(log))
    with pytest.raises(ValueError):
        village.add_citizen("ada")
    with pytest.raises(ValueError):
        village.add_citizen("")
    with pytest.raises(KeyError):
        village.request_wake("ghost", 1, "event")
    with pytest.raises(ValueError):
        village.request_wake("ada", 0, "event")
    with pytest.raises(ValueError):
        village.sleep("ada")
    with pytest.raises(KeyError):
        village.sleep("ghost")
    assert (village.state(), len(log)) == before


def test_sleep_until_a_past_tick_is_rejected_without_logging(tmp_path):
    village, log = make(tmp_path, names=("ada",))
    village.request_wake("ada", 1, "event")
    village.step()
    before = (village.state(), len(log))
    with pytest.raises(ValueError):
        village.sleep("ada", until=0)
    assert (village.state(), len(log)) == before


def test_construction_is_validated(tmp_path):
    log = EventLog(tmp_path / "v.jsonl")
    with pytest.raises(ValueError):
        Village(log, SimClock(), random.Random(0), 0)
    log.append("born", "village", {"citizen": "ada"})
    with pytest.raises(ValueError):
        Village(log, SimClock(), random.Random(0), 1)
