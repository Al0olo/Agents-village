import pytest

from agent_village.analysis import sign_flip_test
from agent_village.power import blocks_needed, power, sign_flip_p


def test_the_flip_p_value_matches_the_exact_one_when_it_enumerates():
    differences = [0.3, -0.1, 0.25, 0.4, -0.05, 0.2, 0.15, 0.35]
    assert sign_flip_p(differences, flips=0, seed=1) == pytest.approx(sign_flip_test(differences))


def test_the_flip_p_value_is_a_monte_carlo_estimate_above_the_exact_limit():
    differences = [0.2] * 22 + [-0.2] * 12
    estimate = sign_flip_p(differences, flips=2000, seed=1, exact_up_to=10)
    assert 0.05 < estimate < 0.5
    assert estimate == sign_flip_p(differences, flips=2000, seed=1, exact_up_to=10)
    assert estimate != sign_flip_p(differences, flips=2000, seed=2, exact_up_to=10)


def test_the_flip_p_value_counts_the_observed_pattern_so_it_is_never_zero():
    assert sign_flip_p([1.0] * 30, flips=100, seed=1, exact_up_to=10) >= 1 / 101


def test_with_no_effect_a_test_at_five_percent_rejects_about_five_percent_of_the_time():
    rate = power(0.0, 0.3, blocks=12, seed=1, reps=400)
    assert 0.01 < rate < 0.12


def test_power_rises_with_the_number_of_blocks_and_with_the_effect():
    low = power(0.15, 0.3, blocks=6, seed=1, reps=300)
    more = power(0.15, 0.3, blocks=24, seed=1, reps=300)
    bigger = power(0.3, 0.3, blocks=6, seed=1, reps=300)
    assert more > low + 0.2 and bigger > low + 0.2


def test_power_is_reproducible_for_a_seed():
    assert power(0.2, 0.3, blocks=10, seed=4, reps=100) == power(
        0.2, 0.3, blocks=10, seed=4, reps=100
    )


def test_blocks_needed_is_the_smallest_number_that_reaches_the_target():
    n = blocks_needed(0.3, 0.2, seed=1, reps=300, limit=30)
    assert 3 <= n <= 12
    assert power(0.3, 0.2, n, seed=1, reps=300) >= 0.8
    assert n == 3 or power(0.3, 0.2, n - 1, seed=1, reps=300) < 0.8


def test_blocks_needed_is_none_when_the_limit_is_too_small():
    assert blocks_needed(0.05, 0.4, seed=1, reps=100, limit=8) is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"effect": 0.1, "spread": 0.0, "blocks": 5},
        {"effect": 0.1, "spread": 0.3, "blocks": 0},
        {"effect": 0.1, "spread": 0.3, "blocks": 5, "alpha": 0.0},
        {"effect": 0.1, "spread": 0.3, "blocks": 5, "reps": 0},
    ],
)
def test_nonsense_inputs_are_refused(kwargs):
    with pytest.raises(ValueError):
        power(seed=1, **kwargs)


def test_a_target_must_be_a_probability():
    with pytest.raises(ValueError):
        blocks_needed(0.1, 0.3, seed=1, target=1.0)


def test_a_sample_exactly_at_the_exact_limit_is_still_tested_exactly():
    differences = [0.3, -0.1, 0.25, 0.4, -0.05, 0.2, 0.15, 0.35]
    assert sign_flip_p(differences, flips=5, seed=1, exact_up_to=8) == sign_flip_test(differences)
    assert sign_flip_p(differences, flips=5, seed=1, exact_up_to=7) != sign_flip_test(differences)


def test_a_power_exactly_at_the_target_is_enough(monkeypatch):
    monkeypatch.setattr(
        "agent_village.power.power",
        lambda effect, spread, blocks, seed, reps, alpha: 0.8 if blocks >= 9 else 0.5,
    )
    assert blocks_needed(0.1, 0.3, seed=1, target=0.8, limit=30) == 9


def test_three_blocks_are_returned_when_three_already_reach_the_target(monkeypatch):
    monkeypatch.setattr("agent_village.power.power", lambda *args: 0.95)
    assert blocks_needed(0.1, 0.3, seed=1, limit=30) == 3
