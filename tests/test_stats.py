import pytest
from stats import per_question, wilson


def test_known_value_27_of_30():
    # Calculé à la main : p = 0,9 ; n = 30 ; z = 1,96 -> environ 74,4 % à 96,5 %
    low, high = wilson(27, 30)
    assert low == pytest.approx(0.744, abs=0.001)
    assert high == pytest.approx(0.965, abs=0.001)


def test_zero_successes_gives_a_real_interval():
    low, high = wilson(0, 30)
    assert low == 0.0
    assert high > 0.1  # pas un intervalle réduit à 0, contrairement à Wald


def test_all_successes_never_exceeds_one():
    low, high = wilson(30, 30)
    assert high == 1.0
    assert low < 1.0


@pytest.mark.parametrize("k", range(0, 11))
def test_interval_stays_between_0_and_1_and_contains_p(k):
    low, high = wilson(k, 10)
    assert 0.0 <= low <= k / 10 <= high <= 1.0


def test_bigger_sample_gives_narrower_interval():
    low_small, high_small = wilson(9, 10)
    low_big, high_big = wilson(90, 100)
    assert high_big - low_big < high_small - low_small


def test_empty_sample_is_refused():
    with pytest.raises(ValueError):
        wilson(0, 0)


def test_per_question_uses_majority_of_runs():
    rows = [
        # question 1 : juste 2 fois sur 3 -> compte comme juste
        {"candidate": "systeme", "task": 1, "verdict": "juste"},
        {"candidate": "systeme", "task": 1, "verdict": "juste"},
        {"candidate": "systeme", "task": 1, "verdict": "refusé"},
        # question 2 : juste 1 fois sur 3 -> ne compte pas
        {"candidate": "systeme", "task": 2, "verdict": "faux"},
        {"candidate": "systeme", "task": 2, "verdict": "juste"},
        {"candidate": "systeme", "task": 2, "verdict": "refusé"},
    ]
    result = per_question(rows, "systeme", "juste")
    assert result["k"] == 1
    assert result["n"] == 2
