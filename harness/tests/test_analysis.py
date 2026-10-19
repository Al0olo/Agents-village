import math

import pytest

from agent_village.analysis import (
    Contrast,
    bootstrap_interval,
    cohens_dz,
    contrast,
    holm,
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
        sign_flip_test([1.0] * 25)


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
