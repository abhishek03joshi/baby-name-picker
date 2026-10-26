import pytest

from name_picker.picker import run_session


NAMES = ["Aarav", "Milo", "Theo", "Leo"]


def test_seed_makes_a_run_reproducible():
    first = run_session(NAMES, 20, seed=42)
    second = run_session(NAMES, 20, seed=42)
    assert first == second


def test_every_round_is_best_of_three_and_scores_add_up():
    result = run_session(NAMES, 25, seed=7)
    assert len(result.rounds) == 25
    assert all(len(round_result.finalists) == 3 for round_result in result.rounds)
    assert sum(result.scores.values()) == 25


def test_two_names_use_three_slots_with_replacement():
    result = run_session(["A", "B"], 10, seed=3)
    assert len(result.rounds) == 10
    assert all(len(round_result.finalists) == 3 for round_result in result.rounds)
    assert all(set(round_result.finalists) <= {"A", "B"} for round_result in result.rounds)
    assert sum(result.scores.values()) == 10


def test_more_than_ten_names_is_rejected():
    names = [f"Name {number}" for number in range(11)]
    with pytest.raises(ValueError, match="at most 10"):
        run_session(names, 2)


@pytest.mark.parametrize("names, tries, message", [
    (["A"], 2, "at least 2"),
    (["A", "A", "B"], 2, "unique"),
    (["A", "B", "C"], 0, "between 1 and 100"),
    (["A", "B", "C"], 101, "between 1 and 100"),
])
def test_invalid_input_is_rejected(names, tries, message):
    with pytest.raises(ValueError, match=message):
        run_session(names, tries)
