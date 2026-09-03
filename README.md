# chipfiring

> Unified interface for visualization and analysis of chip firing games and related algorithms.

[![Latest Version on PyPI](https://img.shields.io/pypi/v/chipfiring.svg)](https://pypi.org/project/chipfiring/)
[![Build Status](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml/badge.svg)](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml)
[![Documentation Status](https://readthedocs.org/projects/chipfiring/badge/?version=latest)](https://chipfiring.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/DhyeyMavani2003/chipfiring/badge.svg?branch=main)](https://coveralls.io/github/DhyeyMavani2003/chipfiring?branch=main)
[![PyPI Downloads](https://static.pepy.tech/badge/chipfiring)](https://pepy.tech/projects/chipfiring)

A Python implementation of the chip-firing game (also known as the dollar game) on graphs. This package provides a mathematical framework for studying and experimenting with chip-firing games, with a focus on the dollar game variant.

## Documentation

Visit [Read the Docs](https://chipfiring.readthedocs.io/en/latest/) for the full
documentation, including overviews and several examples. Repository-specific
guides are available in the
[changelog](https://github.com/DhyeyMavani2003/chipfiring/blob/main/CHANGELOG.md),
[contributing guide](https://github.com/DhyeyMavani2003/chipfiring/blob/main/docs/contributing.md),
and [examples directory](https://github.com/DhyeyMavani2003/chipfiring/tree/main/examples).

## Overview

The chip-firing game is a mathematical model that can be used to study various phenomena in graph theory, algebraic geometry, and other areas of mathematics. In the dollar game variant, we consider a graph where:

- Vertices represent people
- Edges represent relationships between people
- Each vertex has an integer value representing wealth (negative values indicate debt)
- Players can perform lending/borrowing moves by sending money across edges

The goal is to find a sequence of moves that makes everyone debt-free. If such a sequence exists, the game is said to be *winnable*.

## Installation

`chipfiring` requires Python 3.8 or newer.

```bash
pip install chipfiring
```

## Usage

Here is a complete example using the current public API:

```python
from chipfiring import CFDivisor, CFGraph, is_q_reduced, is_winnable, q_reduction

vertices = {"Alice", "Bob", "Charlie", "Elise"}
edges = [
    ("Alice", "Bob", 1),
    ("Alice", "Charlie", 1),
    ("Alice", "Elise", 2),
    ("Bob", "Charlie", 1),
    ("Charlie", "Elise", 1),
]
graph = CFGraph(vertices, edges)
divisor = CFDivisor(
    graph,
    [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)],
)

print(is_winnable(divisor))

bob_reduced = q_reduction(divisor, q_name="Bob")
print(is_q_reduced(bob_reduced, q_name="Bob"))
```

The predicate and reduction helpers operate on a copy and do not mutate the
supplied divisor. The same holds for `DharAlgorithm`, `GreedyAlgorithm`, and
the rank and gonality helpers: every algorithm works on a private copy that
stays attached to the caller's graph object, and only the explicit move methods
(`lending_move`, `borrowing_move`, `set_fire`, `chip_transfer`) change a divisor
in place. Use `CFDivisor.copy()` when you need an independent divisor for such
moves. `CFGraph` equality is structural, so `linear_equivalence` also accepts
divisors on independently constructed copies of the same graph. If `q_name` is
omitted, `q_reduction` preserves the historical most-indebted-vertex heuristic.
Use `q_reduction_with_root` when the automatically chosen root is needed for a
later `is_q_reduced` check.

## Mathematical Background

The package uses the standard divisor theory of finite graphs, including:

1. **Graph Structure**: Finite, connected, undirected multigraphs without loop edges
2. **Divisors**: Elements of the free abelian group on vertices
3. **Laplacian Matrix**: Matrix representation of lending moves
4. **Linear Equivalence**: Equivalence relation on divisors
5. **Effective Divisors**: Divisors with non-negative values
6. **Winnability**: Property of being linearly equivalent to an effective divisor

## Features

- Mathematical graph implementation with support for multigraphs
- Divisor class with operations for lending and borrowing
- Laplacian matrix computations
- Linear equivalence checking
- Set-firing moves
- Winnability and explicit q-reduction
- Baker-Norine rank and graph gonality helpers
- Dhar's burning algorithm and graph orientations
- Interactive graph and divisor visualization
- Type hints and API documentation

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/DhyeyMavani2003/chipfiring.git
cd chipfiring

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements.docs.txt

# Run the regression tests and package doctests
python -m pytest -q
python -m pytest --doctest-modules chipfiring -q

# Verify the saved-output examples
make check-example-outputs PYTHON=python

# Build documentation
cd docs
make html
```

## License

This project is licensed under the MIT License; see
[LICENSE.txt](https://github.com/DhyeyMavani2003/chipfiring/blob/main/LICENSE.txt).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
