import itertools
import math
import random

import pytest

from agent_village.analysis import (
    FLIPS,
    MAX_EXACT,
    Contrast,
    bootstrap_interval,
    cohens_dz,
    contrast,
    flip_estimate,
    holm,
    p_value,
    paired_differences,
    sign_flip_test,
)


def test_paired_differences_are_within_blocks_and_skip_blocks_missing_an_arm():
    values = {
        0: {"A": 0.5, "D": 0.25, "B": 0.4},
        1: {"A": 0.75, "D": 0.5},
        2: {"A": 0.5},
    }
    assert paired_differences(values, "D", "A") == {0: -0.25, 1: -0.25}
    assert paired_differences(values, "B", "A") == {0: pytest.approx(-0.1)}


def test_an_exact_sign_flip_test_has_the_smallest_possible_p_for_its_size():
    for n in (2, 3, 5, 8):
        assert sign_flip_test([1.0] * n) == pytest.approx(2 / 2**n)


def test_the_test_is_two_sided_and_symmetric():
    diffs = [0.5, -0.25, 1.0, 0.75, -0.125]
    assert sign_flip_test(diffs) == pytest.approx(sign_flip_test([-d for d in diffs]))


def test_a_known_small_case_by_hand():
    # Flips of [1, 2, 3] give sums -6 -4 -2 0 0 2 4 6: |sum| >= 6 in 2 of 8, >= 4 in 4 of 8.
    assert sign_flip_test([1, 2, 3]) == pytest.approx(0.25)
    assert sign_flip_test([1, 1, 2]) == pytest.approx(0.25)
    assert sign_flip_test([1, -1, 2]) == pytest.approx(0.75)


def test_no_difference_gives_p_one():
    assert sign_flip_test([0.0, 0.0, 0.0]) == 1.0
    assert sign_flip_test([0.5, -0.5]) == 1.0


def test_the_floor_for_ten_paired_blocks_is_far_below_the_unpaired_floor():
    assert sign_flip_test([0.1] * 10) < 0.002
    assert sign_flip_test([0.1] * 4) == pytest.approx(0.125)


def test_a_test_needs_differences():
    with pytest.raises(ValueError):
        sign_flip_test([])


def test_too_many_blocks_to_enumerate_is_refused():
    with pytest.raises(ValueError):
        sign_flip_test([1.0] * (MAX_EXACT + 1))


def brute_force(differences):
    observed = abs(sum(differences))
    flips = list(itertools.product((1, -1), repeat=len(differences)))
    hits = sum(
        abs(sum(s * d for s, d in zip(signs, differences, strict=True))) >= observed - 1e-12
        for signs in flips
    )
    return hits / len(flips)


@pytest.mark.parametrize("n", range(1, 13))
def test_the_exact_test_matches_a_brute_force_enumeration(n):
    rng = random.Random(n)
    for _ in range(5):
        differences = [round(rng.uniform(-1, 1), 3) for _ in range(n)]
        assert sign_flip_test(differences) == pytest.approx(brute_force(differences), abs=1e-12)


def test_the_exact_test_handles_ties_zeros_and_an_odd_number_of_blocks():
    assert sign_flip_test([0.0] * 7) == 1.0
    assert sign_flip_test([0.5, 0.5, 0.5, 0.0, 0.0]) == pytest.approx(
        brute_force([0.5, 0.5, 0.5, 0.0, 0.0])
    )
    assert sign_flip_test([0.1, -0.1, 0.1, -0.1, 0.1]) == pytest.approx(
        brute_force([0.1, -0.1, 0.1, -0.1, 0.1])
    )


def test_thirty_blocks_all_the_same_way_reach_the_floor_exactly():
    assert sign_flip_test([0.2] * 30) == 2 / 2**30
    assert sign_flip_test([0.2] * 29 + [-0.2]) == 2 * 31 / 2**30


def test_the_limit_is_high_enough_for_a_main_run_of_forty_blocks():
    assert MAX_EXACT >= 40
    rng = random.Random(1)
    p = sign_flip_test([rng.gauss(0.1, 0.3) for _ in range(40)])
    assert 0 < p <= 1


def test_the_effect_size_is_the_mean_over_the_standard_deviation():
    assert cohens_dz([1.0, 2.0, 3.0]) == pytest.approx(2.0)
    assert cohens_dz([0.5, 0.5, 0.5]) is None
    assert cohens_dz([1.0]) is None


def test_a_bootstrap_interval_is_reproducible_and_brackets_the_mean():
    diffs = [0.1, 0.3, 0.2, 0.4, 0.25, 0.15]
    low, high = bootstrap_interval(diffs, seed=1)
    assert (low, high) == bootstrap_interval(diffs, seed=1)
    assert low <= sum(diffs) / len(diffs) <= high
    assert min(diffs) <= low and high <= max(diffs)
    assert bootstrap_interval(diffs, seed=2) != (low, high)


def test_the_bootstrap_interval_of_identical_differences_is_a_point():
    assert bootstrap_interval([0.2] * 5, seed=0) == (pytest.approx(0.2), pytest.approx(0.2))


def test_a_wider_spread_gives_a_wider_interval():
    tight = bootstrap_interval([0.2, 0.21, 0.19, 0.2, 0.2], seed=3)
    wide = bootstrap_interval([0.0, 0.4, 0.1, 0.3, 0.2], seed=3)
    assert wide[1] - wide[0] > tight[1] - tight[0]


def test_a_bootstrap_needs_differences_and_a_sensible_level():
    with pytest.raises(ValueError):
        bootstrap_interval([], seed=0)
    with pytest.raises(ValueError):
        bootstrap_interval([1.0], seed=0, level=1.0)


def test_holm_adjusts_by_rank_and_keeps_order_and_monotonicity():
    adjusted = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adjusted["a"] == pytest.approx(0.03)
    assert adjusted["c"] == pytest.approx(0.06)
    assert adjusted["b"] == pytest.approx(0.06)


def test_holm_never_exceeds_one_and_a_single_test_is_unchanged():
    assert holm({"a": 0.5, "b": 0.9}) == {"a": 1.0, "b": 1.0}
    assert holm({"only": 0.03}) == {"only": 0.03}
    assert holm({}) == {}


def test_holm_rejects_probabilities_outside_zero_and_one():
    with pytest.raises(ValueError):
        holm({"a": 1.2})


def test_the_standard_deviation_used_is_the_sample_one():
    diffs = [2.0, 4.0]
    assert cohens_dz(diffs) == pytest.approx(3.0 / math.sqrt(2.0))


def test_a_contrast_reports_everything_the_registration_asks_for():
    values = {b: {"D": 0.2 + 0.01 * b, "A": 0.5} for b in range(6)}
    result = contrast(values, "D", "A", seed=1)
    assert isinstance(result, Contrast)
    assert result.blocks == 6 and result.first == "D" and result.second == "A"
    assert result.mean_difference == pytest.approx(-0.275)
    assert result.p == pytest.approx(2 / 2**6)
    assert result.interval[0] <= result.mean_difference <= result.interval[1]
    assert result.dz is not None and result.dz < 0


def test_a_contrast_of_arms_that_never_share_a_block_is_refused():
    with pytest.raises(ValueError):
        contrast({0: {"A": 0.1}, 1: {"D": 0.2}}, "D", "A", seed=1)


def test_a_monte_carlo_p_value_counts_the_observed_pattern_and_is_reproducible():
    differences = [0.2] * 22 + [-0.2] * 12
    estimate = flip_estimate(differences, flips=2000, seed=1)
    assert 0.05 < estimate < 0.5
    assert estimate == flip_estimate(differences, flips=2000, seed=1)
    assert flip_estimate([1.0] * 30, flips=100, seed=1) >= 1 / 101


def test_the_registered_p_value_is_exact_up_to_the_limit_and_sampled_beyond_it():
    small = [0.3, -0.1, 0.25, 0.4, -0.05, 0.2, 0.15, 0.35]
    assert p_value(small, seed=1) == sign_flip_test(small)
    rng = random.Random(3)
    large = [rng.gauss(0.2, 0.3) for _ in range(MAX_EXACT + 5)]
    estimate = p_value(large, seed=1)
    assert 0 < estimate < 0.05
    assert estimate == p_value(large, seed=1)
    assert FLIPS == 100_000


def test_a_contrast_over_more_blocks_than_the_exact_limit_still_reports_everything():
    values = {n: {"D": 0.3, "A": 0.5 + (n % 3) * 0.01} for n in range(MAX_EXACT + 5)}
    result = contrast(values, "D", "A", seed=1)
    assert result.blocks == MAX_EXACT + 5 and result.p < 0.001


def test_the_exact_limit_is_forty_blocks_and_forty_are_still_exact():
    assert MAX_EXACT == 40
    assert p_value([0.2] * 40, seed=1) == 2 / 2**40


def test_a_monte_carlo_p_value_for_a_certain_pattern_is_one_over_flips_plus_one():
    assert flip_estimate([1.0] * 30, flips=100, seed=1) == 1 / 101
