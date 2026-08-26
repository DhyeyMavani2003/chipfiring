"""Explore gonality on a family of genus-5 chains of cycles.

The default cycle lengths 2, 3, 4, and 5 give 4^5 = 1024 exhaustive
computations. Expected values follow the genus-5 chain-of-cycles formula in
Jensen and Lehmann, "Scrollar Invariants of Tropical Curves." Use ``--limit``
for a quick smoke test.
"""

from __future__ import annotations

import argparse
import itertools
import time
from typing import Iterable, List, Sequence, Tuple

from chipfiring import CFGraph, gonality


def _validate_cycle_lengths(cycle_lengths: Sequence[int]) -> None:
    if not cycle_lengths or not all(
        type(length) is int and length >= 2 for length in cycle_lengths
    ):
        raise ValueError("Cycle lengths must be integers at least 2.")


def chain(cycle_lengths: Sequence[int]) -> CFGraph:
    """Build a unit-edge chain of cycles."""
    _validate_cycle_lengths(cycle_lengths)

    vertices = {
        f"z_{i + 1}_{j}"
        for i, length in enumerate(cycle_lengths)
        for j in range(length)
    }
    edges = []
    for i, length in enumerate(cycle_lengths):
        if length == 2:
            edges.append((f"z_{i + 1}_0", f"z_{i + 1}_1", 2))
        else:
            for j in range(length):
                edges.append(
                    (f"z_{i + 1}_{j}", f"z_{i + 1}_{(j + 1) % length}", 1)
                )

    for i, length in enumerate(cycle_lengths):
        if i > 0:
            edges.append((f"z_{i}_0", f"z_{i + 1}_{length - 1}", 1))

    return CFGraph(vertices, edges)


def expected_gonality(cycle_lengths: Sequence[int]) -> int:
    """Return the expected genus-5 gonality for this chain construction."""
    if len(cycle_lengths) != 5:
        raise ValueError("The expected formula requires exactly five cycles.")
    _validate_cycle_lengths(cycle_lengths)
    if tuple(cycle_lengths[1:4]) == (2, 2, 2):
        return 2
    if (
        cycle_lengths[1] == 2
        or cycle_lengths[2] == 3
        or cycle_lengths[3] == 2
    ):
        return 3
    return 4


def cases(lengths: Sequence[int]) -> Iterable[Tuple[int, ...]]:
    return itertools.product(lengths, repeat=5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lengths",
        default="2,3,4,5",
        help="comma-separated cycle lengths (default: 2,3,4,5)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="run only the first N cases for a quick smoke test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lengths = [int(value) for value in args.lengths.split(",")]
    selected_cases = cases(lengths)
    if args.limit is not None:
        selected_cases = itertools.islice(selected_cases, args.limit)

    started = time.perf_counter()
    checked = 0
    mismatches: List[Tuple[List[int], int, int]] = []

    for cycle_lengths_tuple in selected_cases:
        cycle_lengths = list(cycle_lengths_tuple)
        expected = expected_gonality(cycle_lengths)
        computed = gonality(chain(cycle_lengths)).gonality
        agrees = expected == computed
        print(
            cycle_lengths,
            f"Expected: {expected}",
            f"Computed: {computed}",
            agrees,
        )
        checked += 1
        if not agrees:
            mismatches.append((cycle_lengths, expected, computed))

    elapsed = time.perf_counter() - started
    print(
        f"SUMMARY checked={checked} mismatches={len(mismatches)} "
        f"elapsed_seconds={elapsed:.3f}"
    )
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
