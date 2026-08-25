import pytest

from examples.paper_chain_of_cycles import expected_gonality


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
