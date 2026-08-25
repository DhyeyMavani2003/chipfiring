import pytest

from examples.chain_of_cycles_gonality import expected_gonality


@pytest.mark.parametrize(
    ("cycle_lengths", "expected"),
    [
        ([2, 2, 2, 2, 2], 2),
        ((2, 2, 2, 2, 2), 2),
        ([2, 2, 4, 5, 2], 3),
        ((2, 3, 4, 5, 2), 4),
    ],
)
def test_expected_gonality_accepts_sequence_types(cycle_lengths, expected):
    assert expected_gonality(cycle_lengths) == expected


def test_expected_gonality_requires_five_cycles():
    with pytest.raises(ValueError, match="exactly five cycles"):
        expected_gonality([2, 2, 2, 2])


@pytest.mark.parametrize(
    "cycle_lengths",
    [
        [1, 2, 2, 2, 1],
        [2, 2, 2, 2, "bad"],
        [2, 2, 2, 2, True],
    ],
)
def test_expected_gonality_validates_cycle_lengths(cycle_lengths):
    with pytest.raises(ValueError, match="integers at least 2"):
        expected_gonality(cycle_lengths)
